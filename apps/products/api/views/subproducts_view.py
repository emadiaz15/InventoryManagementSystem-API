from decimal import Decimal, InvalidOperation
import logging

from django.db import transaction
from django.db.models import OuterRef, Subquery, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.core.pagination import Pagination
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.api.repositories.subproduct_repository import SubproductRepository
from apps.products.docs.subproduct_doc import (
    list_subproducts_doc,
    create_subproduct_doc,
    get_subproduct_by_id_doc,
    update_subproduct_by_id_doc,
    delete_subproduct_by_id_doc
)
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.models import SubproductStock
from apps.stocks.services import initialize_subproduct_stock, adjust_subproduct_stock

logger = logging.getLogger(__name__)


@extend_schema(**list_subproducts_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subproduct_list(request, prod_pk):
    """
    Lista subproductos activos de un producto padre, con paginación
    e incluyendo el stock actual calculado.
    """
    parent = get_object_or_404(Product, pk=prod_pk, status=True)

    stock_sq = SubproductStock.objects.filter(
        subproduct=OuterRef('pk'), status=True
    ).values('quantity')[:1]

    qs = SubproductRepository.get_all_active(parent.pk).annotate(
        current_stock_val=Subquery(stock_sq, output_field=DecimalField(max_digits=15, decimal_places=2))
    ).annotate(
        current_stock=Coalesce('current_stock_val', Decimal('0.00'), output_field=DecimalField(max_digits=15, decimal_places=2))
    )

    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = SubProductSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_subproduct_doc)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_subproduct(request, prod_pk):
    """
    Crea un nuevo subproducto e inicializa su stock.
    Solo administradores.
    """
    parent = get_object_or_404(Product, pk=prod_pk, status=True)
    data = request.data.copy()
    data.setdefault('initial_stock_reason', 'Stock Inicial por Creación Subproducto')
    data.setdefault('initial_stock_location', None)

    # Validar cantidad inicial
    qty_str = data.pop('initial_stock_quantity', '0')
    try:
        initial_qty = Decimal(qty_str)
        if initial_qty < 0:
            raise ValueError("Cantidad negativa")
    except (InvalidOperation, ValueError):
        raise serializers.ValidationError({
            "initial_stock_quantity": f"Valor inválido ('{qty_str}') para cantidad inicial."
        })

    serializer = SubProductSerializer(data=data, context={'request': request, 'parent_product': parent})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            subp = serializer.save(user=request.user)
            initialize_subproduct_stock(
                subproduct=subp,
                user=request.user,
                initial_quantity=initial_qty,
                location=data.get('initial_stock_location'),
                reason=data.get('initial_stock_reason')
            )
    except Exception as e:
        logger.error(f"Error creando subproducto: {e}")
        detail = getattr(e, 'detail', str(e))
        return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)

    # Re-anotar stock para la respuesta
    annotated = Subproduct.objects.annotate(
        current_stock_val=Subquery(
            SubproductStock.objects.filter(subproduct=subp, status=True)
            .values('quantity')[:1],
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    ).annotate(
        current_stock=Coalesce('current_stock_val', Decimal('0.00'), output_field=DecimalField(max_digits=15, decimal_places=2))
    ).get(pk=subp.pk)

    resp_ser = SubProductSerializer(annotated, context={'request': request, 'parent_product': parent})
    return Response(resp_ser.data, status=status.HTTP_201_CREATED)


@extend_schema(**get_subproduct_by_id_doc)
@extend_schema(**update_subproduct_by_id_doc)
@extend_schema(**delete_subproduct_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def subproduct_detail(request, prod_pk, subp_pk):
    """
    GET   → consulta (autenticados).  
    PUT   → actualización stock/opcional (solo staff).  
    DELETE→ baja suave (solo staff).
    """
    parent = get_object_or_404(Product, pk=prod_pk, status=True)

    # GET
    if request.method == 'GET':
        stock_sq = SubproductStock.objects.filter(subproduct=OuterRef('pk'), status=True).values('quantity')[:1]
        qs = Subproduct.objects.annotate(
            current_stock_val=Subquery(stock_sq, output_field=DecimalField(max_digits=15, decimal_places=2))
        ).annotate(
            current_stock=Coalesce('current_stock_val', Decimal('0.00'), output_field=DecimalField(max_digits=15, decimal_places=2))
        )
        instance = get_object_or_404(qs, pk=subp_pk, parent=parent)
        ser = SubProductSerializer(instance, context={'request': request, 'parent_product': parent})
        return Response(ser.data)

    # Carga instancia para PUT/DELETE
    instance = get_object_or_404(Subproduct, pk=subp_pk, parent=parent, status=True)

    # PUT
    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para actualizar este subproducto."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = SubProductSerializer(instance, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                updated = serializer.save(user=request.user)
                qty_change = serializer.validated_data.get('quantity_change')
                reason     = serializer.validated_data.get('reason')
                if qty_change is not None:
                    stock_rec = SubproductStock.objects.select_for_update().get(subproduct=updated, location=None, status=True)
                    adjust_subproduct_stock(
                        subproduct_stock=stock_rec,
                        quantity_change=qty_change,
                        reason=reason,
                        user=request.user
                    )
        except Exception as e:
            logger.error(f"Error actualizando subproducto {subp_pk}: {e}")
            detail = getattr(e, 'detail', str(e))
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)

        resp_ser = SubProductSerializer(updated, context={'request': request, 'parent_product': parent})
        return Response(resp_ser.data)

    # DELETE
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para eliminar este subproducto."},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            instance.delete(user=request.user)
        except Exception as e:
            logger.error(f"Error eliminando subproducto {subp_pk}: {e}")
            return Response({"detail": "Error interno al eliminar el subproducto."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_204_NO_CONTENT)
