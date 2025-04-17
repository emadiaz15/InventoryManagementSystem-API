from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal, InvalidOperation

# --- ORM, Modelos Stock, etc. ---
from django.db.models import OuterRef, Subquery, DecimalField
from django.db.models.functions import Coalesce
from apps.stocks.models import SubproductStock

# --- Otros Imports ---
from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.api.repositories.subproduct_repository import SubproductRepository
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.products.docs.subproduct_doc import (
    list_subproducts_doc, create_subproduct_doc, get_subproduct_by_id_doc,
    update_subproduct_by_id_doc, delete_subproduct_by_id_doc
)
from apps.stocks.services import initialize_subproduct_stock, adjust_subproduct_stock


@extend_schema(**list_subproducts_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def subproduct_list(request, prod_pk):
    """
    Lista subproductos activos de un producto padre, con paginación,
    e incluyendo el stock actual calculado.
    """
    parent_product = get_object_or_404(Product, pk=prod_pk, status=True)

    subproduct_stock_sq = SubproductStock.objects.filter(
        subproduct=OuterRef('pk'), status=True
    ).values('quantity')[:1]

    subproducts_qs = SubproductRepository.get_all_active(parent_product.pk).annotate(
        current_stock_val=Subquery(subproduct_stock_sq, output_field=DecimalField(max_digits=15, decimal_places=2))
    ).annotate(
        current_stock=Coalesce('current_stock_val', Decimal('0.00'), output_field=DecimalField(max_digits=15, decimal_places=2))
    )

    paginator = Pagination()
    paginated = paginator.paginate_queryset(subproducts_qs, request)
    serializer = SubProductSerializer(paginated, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_subproduct_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_subproduct(request, prod_pk):
    """
    Crea un nuevo subproducto, inicializa su stock,
    y actualiza el flag del producto padre si es necesario.
    """
    parent_product = get_object_or_404(Product, pk=prod_pk, status=True)
    serializer_context = {'request': request, 'parent_product': parent_product}

    request_data = request.data.copy()
    initial_qty_str = request_data.pop('initial_stock_quantity', '0')
    initial_loc = request_data.pop('initial_stock_location', None)
    initial_reason = "Stock Inicial por Creación Subproducto"

    try:
        initial_qty = Decimal(initial_qty_str)
        if initial_qty < 0:
            raise ValueError("Cantidad negativa")
    except (InvalidOperation, ValueError):
        raise serializers.ValidationError({"initial_stock_quantity": f"Valor inválido ('{initial_qty_str}')"})

    serializer = SubProductSerializer(data=request_data, context=serializer_context)

    if serializer.is_valid():
        try:
            with transaction.atomic():
                subproduct_instance = serializer.save(user=request.user)

                initial_reason = f"Stock Inicial por Creación Subproducto #{subproduct_instance.pk}"

                initialize_subproduct_stock(
                    subproduct=subproduct_instance,
                    user=request.user,
                    initial_quantity=initial_qty,
                    location=initial_loc,
                    reason=initial_reason
                )

                if parent_product.has_individual_stock:
                    parent_product.has_individual_stock = False
                    parent_product.save(user=request.user, update_fields=['has_individual_stock', 'modified_at', 'modified_by'])

            annotated = Subproduct.objects.annotate(
                current_stock_val=Subquery(
                    SubproductStock.objects.filter(subproduct=subproduct_instance, status=True).values('quantity')[:1],
                    output_field=DecimalField(decimal_places=2)
                )
            ).annotate(
                current_stock=Coalesce('current_stock_val', Decimal('0.00'), output_field=DecimalField(decimal_places=2))
            ).get(pk=subproduct_instance.pk)

            response_serializer = SubProductSerializer(annotated, context=serializer_context)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except (ValidationError, serializers.ValidationError, ValueError, Exception) as e:
            print(f"Error al crear subproducto: {e}")
            detail = getattr(e, 'detail', str(e)) if isinstance(e, (serializers.ValidationError, ValidationError)) else "Error interno"
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_subproduct_by_id_doc)
@extend_schema(**update_subproduct_by_id_doc)
@extend_schema(**delete_subproduct_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def subproduct_detail(request, prod_pk, subp_pk):
    """
    Obtiene (GET), actualiza (PUT) o elimina (DELETE) un subproducto.
    """
    parent_product = get_object_or_404(Product, pk=prod_pk, status=True)

    if request.method == 'GET':
        stock_sq = SubproductStock.objects.filter(subproduct=OuterRef('pk'), status=True).values('quantity')[:1]
        queryset = Subproduct.objects.annotate(
            current_stock_val=Subquery(stock_sq, output_field=DecimalField(max_digits=15, decimal_places=2))
        ).annotate(
            current_stock=Coalesce('current_stock_val', Decimal('0.00'), output_field=DecimalField(max_digits=15, decimal_places=2))
        )
        instance = get_object_or_404(queryset, pk=subp_pk, parent=parent_product, status=True)
        serializer = SubProductSerializer(instance, context={'request': request})
        return Response(serializer.data)

    instance = get_object_or_404(Subproduct, pk=subp_pk, parent=parent_product, status=True)

    if request.method == 'PUT':
        serializer = SubProductSerializer(instance, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            validated_data = serializer.validated_data
            quantity_change = validated_data.get('quantity_change')
            reason = validated_data.get('reason')

            try:
                with transaction.atomic():
                    updated = serializer.save(user=request.user)

                    if quantity_change is not None:
                        try:
                            stock_record = SubproductStock.objects.select_for_update().get(
                                subproduct=updated,
                                location=None,
                                status=True
                            )
                            adjust_subproduct_stock(
                                subproduct_stock=stock_record,
                                quantity_change=quantity_change,
                                reason=reason,
                                user=request.user
                            )
                        except SubproductStock.DoesNotExist:
                            raise ValidationError("No se encontró stock para el subproducto.")
                        except SubproductStock.MultipleObjectsReturned:
                            raise ValidationError("Se encontraron múltiples registros de stock. Especifique ubicación.")

                response_serializer = SubProductSerializer(updated, context={'request': request})
                return Response(response_serializer.data)

            except (ValidationError, serializers.ValidationError, Exception) as e:
                detail = getattr(e, 'detail', str(e)) if isinstance(e, (serializers.ValidationError, ValidationError)) else str(e)
                return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            instance.delete(user=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"Error al eliminar subproducto: {e}")
            return Response({"detail": "Error interno al eliminar el subproducto."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

