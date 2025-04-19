from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import logging

from django.db import transaction
from django.db.models import Sum, F, Case, When, DecimalField, OuterRef, Subquery
from django.shortcuts import get_object_or_404

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.core.pagination import Pagination
from apps.products.api.serializers.product_serializer import ProductSerializer
from apps.products.api.repositories.product_repository import ProductRepository
from apps.stocks.models import ProductStock, SubproductStock
from apps.stocks.services import initialize_product_stock, adjust_product_stock
from apps.products.filters.product_filter import ProductFilter
from apps.products.docs.product_doc import (
    list_product_doc,
    create_product_doc,
    get_product_by_id_doc,
    update_product_by_id_doc,
    delete_product_by_id_doc
)

logger = logging.getLogger(__name__)


@extend_schema(**list_product_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_list(request):
    """
    Lista productos activos con paginación y stock calculado.
    """
    # Subqueries para stock individual y subproductos
    product_stock_sq = ProductStock.objects.filter(
        product=OuterRef('pk'), status=True
    ).values('quantity')[:1]
    subproduct_stock_sum_sq = SubproductStock.objects.filter(
        subproduct__parent_id=OuterRef('pk'),
        status=True,
        subproduct__status=True
    ).values('subproduct__parent').annotate(total=Sum('quantity')).values('total')

    # Query inicial y anotaciones
    qs = ProductRepository.get_all_active_products().annotate(
        individual_stock_qty=Subquery(product_stock_sq, output_field=DecimalField(max_digits=15, decimal_places=2)),
        subproduct_stock_total=Subquery(subproduct_stock_sum_sq, output_field=DecimalField(max_digits=15, decimal_places=2))
    ).annotate(
        current_stock=Case(
            When(has_individual_stock=True, individual_stock_qty__isnull=False, then=F('individual_stock_qty')),
            When(has_individual_stock=False, subproduct_stock_total__isnull=False, then=F('subproduct_stock_total')),
            default=Decimal('0.00'),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    )

    # Filtrado
    filterset = ProductFilter(request.GET, queryset=qs)
    if not filterset.is_valid():
        return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
    qs = filterset.qs

    # Paginación y serialización
    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = ProductSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_product_doc)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_product(request):
    """
    Crea un nuevo producto y, si se indica, inicializa stock.
    Solo administradores.
    """
    data = request.data.copy()
    data['has_individual_stock'] = True

    # Extraer stock inicial
    qty_str = data.pop('initial_stock_quantity', '0')
    if isinstance(qty_str, list):
        qty_str = qty_str[0]
    location = data.pop('initial_stock_location', None)
    reason   = data.pop('initial_stock_reason', 'Stock inicial por creación')

    # Validar cantidad
    try:
        initial_qty = Decimal(qty_str)
        if initial_qty < 0:
            raise serializers.ValidationError({
                "initial_stock_quantity": "La cantidad inicial no puede ser negativa."
            })
    except (InvalidOperation, ValueError):
        raise serializers.ValidationError({
            "initial_stock_quantity": f"Valor inválido ('{qty_str}') para cantidad inicial."
        })

    serializer = ProductSerializer(data=data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            product = serializer.save(user=request.user)
            if product.has_individual_stock:
                initialize_product_stock(
                    product=product,
                    user=request.user,
                    initial_quantity=initial_qty,
                    location=location,
                    reason=reason
                )
    except Exception as e:
        logger.error(f"Error creando producto: {e}")
        detail = getattr(e, 'detail', str(e))
        code = status.HTTP_400_BAD_REQUEST if isinstance(e, serializers.ValidationError) else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response({"detail": detail}, status=code)

    return Response(
        ProductSerializer(product, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )


@extend_schema(**get_product_by_id_doc)
@extend_schema(**update_product_by_id_doc)
@extend_schema(**delete_product_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, prod_pk):
    """
    GET   → consulta (autenticados).  
    PUT   → actualización stock/opcional (solo staff).  
    DELETE→ baja suave (solo staff).
    """
    # ANOTACIÓN PARA GET
    if request.method == 'GET':
        product_qs = ProductRepository.get_all_active_products().annotate(
            individual_stock_qty=Subquery(
                ProductStock.objects.filter(product=OuterRef('pk'), status=True)
                .values('quantity')[:1],
                output_field=DecimalField(max_digits=15, decimal_places=2)
            ),
            subproduct_stock_total=Subquery(
                SubproductStock.objects.filter(
                    subproduct__parent_id=OuterRef('pk'),
                    status=True,
                    subproduct__status=True
                ).values('subproduct__parent')
                 .annotate(total=Sum('quantity'))
                 .values('total'),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        ).annotate(
            current_stock=Case(
                When(has_individual_stock=True, individual_stock_qty__isnull=False, then=F('individual_stock_qty')),
                When(has_individual_stock=False, subproduct_stock_total__isnull=False, then=F('subproduct_stock_total')),
                default=Decimal('0.00'),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        )
        product = get_object_or_404(product_qs, pk=prod_pk)
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)

    # CARGAR INSTANCIA PARA PUT/DELETE
    product = get_object_or_404(ProductRepository.get_by_id(prod_pk))

    # PUT
    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para actualizar este producto."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                updated = serializer.save(user=request.user)
                # Ajuste adicional de stock
                qty_change = serializer.validated_data.get('quantity_change')
                reason     = serializer.validated_data.get('reason')
                if qty_change is not None:
                    if updated.has_individual_stock:
                        stock_rec = ProductStock.objects.select_for_update().get(product=updated, location=None)
                        adjust_product_stock(
                            product_stock=stock_rec,
                            quantity_change=qty_change,
                            reason=reason,
                            user=request.user
                        )
                    else:
                        raise ValidationError("No se puede ajustar stock de un producto con subproductos.")
        except Exception as e:
            logger.error(f"Error actualizando producto {prod_pk}: {e}")
            detail = getattr(e, 'detail', str(e))
            code = status.HTTP_400_BAD_REQUEST if isinstance(e, (serializers.ValidationError, ValidationError)) else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response({"detail": detail}, status=code)

        return Response(ProductSerializer(updated, context={'request': request}).data)

    # DELETE (soft delete)
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para eliminar este producto."},
                status=status.HTTP_403_FORBIDDEN
            )
        product.delete(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
