from django.core.cache import cache
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import logging

from django.db import transaction
from django.db.models import Sum, F, Case, When, DecimalField, OuterRef, Subquery
from django.shortcuts import get_object_or_404

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.cache import cache_page
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

from apps.products.utils.cache_helpers import (
    PRODUCT_LIST_CACHE_PREFIX,
    PRODUCT_DETAIL_CACHE_PREFIX,
    product_list_cache_key,
    product_detail_cache_key,
)
from apps.products.utils.redis_utils import delete_keys_by_pattern

logger = logging.getLogger(__name__)

# --- Listar productos activos con paginación y stock calculado ---
@extend_schema(
    summary=list_product_doc["summary"],
    description=list_product_doc["description"],
    tags=list_product_doc["tags"],
    operation_id=list_product_doc["operation_id"],
    parameters=list_product_doc["parameters"],
    responses=list_product_doc["responses"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60 * 15, key_prefix=PRODUCT_LIST_CACHE_PREFIX)
def product_list(request):
    """
    Endpoint para listar productos activos con paginación y stock calculado.
    """
    product_stock_sq = ProductStock.objects.filter(
        product=OuterRef('pk'), status=True
    ).values('quantity')[:1]
    subproduct_stock_sum_sq = SubproductStock.objects.filter(
        subproduct__parent_id=OuterRef('pk'),
        status=True,
        subproduct__status=True
    ).values('subproduct__parent').annotate(total=Sum('quantity')).values('total')

    qs = ProductRepository.get_all_active_products().annotate(
        individual_stock_qty=Subquery(product_stock_sq, output_field=DecimalField(max_digits=15, decimal_places=2)),
        subproduct_stock_total=Subquery(subproduct_stock_sum_sq, output_field=DecimalField(max_digits=15, decimal_places=2))
    ).annotate(
        current_stock=Case(
            When(has_subproducts=False, individual_stock_qty__isnull=False, then=F('individual_stock_qty')),
            When(has_subproducts=True, subproduct_stock_total__isnull=False, then=F('subproduct_stock_total')),
            default=Decimal('0.00'),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    )

    filterset = ProductFilter(request.GET, queryset=qs)
    if not filterset.is_valid():
        return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
    qs = filterset.qs

    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = ProductSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# --- Crear nuevo producto ---
@extend_schema(
    summary=create_product_doc["summary"],
    description=create_product_doc["description"],
    tags=create_product_doc["tags"],
    operation_id=create_product_doc["operation_id"],
    request=create_product_doc["requestBody"],
    responses=create_product_doc["responses"]
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_product(request):
    """
    Endpoint para crear un nuevo producto y, si se indica, inicializar stock.
    Solo administradores.
    """
    data = request.data.copy()
    data['has_subproducts'] = False

    qty_str = data.pop('initial_stock_quantity', '0')
    if isinstance(qty_str, list):
        qty_str = qty_str[0]
    reason = data.pop('initial_stock_reason', 'Stock inicial por creación')

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
            if not product.has_subproducts:
                initialize_product_stock(
                    product=product,
                    user=request.user,
                    initial_quantity=initial_qty,
                    reason=reason
                )
    except Exception as e:
        logger.error(f"Error creando producto: {e}")
        detail = getattr(e, 'detail', str(e))
        code = status.HTTP_400_BAD_REQUEST if isinstance(e, serializers.ValidationError) else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response({"detail": detail}, status=code)

    # Invalidar todas las páginas cacheadas de product_list
    delete_keys_by_pattern(f"{PRODUCT_LIST_CACHE_PREFIX}*")

    return Response(
        ProductSerializer(product, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )


# --- Obtener, actualizar y eliminar producto por ID ---
@extend_schema(
    summary=get_product_by_id_doc["summary"],
    description=get_product_by_id_doc["description"],
    tags=get_product_by_id_doc["tags"],
    operation_id=get_product_by_id_doc["operation_id"],
    parameters=get_product_by_id_doc["parameters"],
    responses=get_product_by_id_doc["responses"]
)
@extend_schema(
    summary=update_product_by_id_doc["summary"],
    description=update_product_by_id_doc["description"],
    tags=update_product_by_id_doc["tags"],
    operation_id=update_product_by_id_doc["operation_id"],
    parameters=update_product_by_id_doc["parameters"],
    request=update_product_by_id_doc["requestBody"],
    responses=update_product_by_id_doc["responses"]
)
@extend_schema(
    summary=delete_product_by_id_doc["summary"],
    description=delete_product_by_id_doc["description"],
    tags=delete_product_by_id_doc["tags"],
    operation_id=delete_product_by_id_doc["operation_id"],
    parameters=delete_product_by_id_doc["parameters"],
    responses=delete_product_by_id_doc["responses"]
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, prod_pk):
    product = ProductRepository.get_by_id(prod_pk)
    if not product:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    cache_key_detail = product_detail_cache_key(prod_pk)

    # GET con cache específico de detalle
    if request.method == 'GET':
        @cache_page(60 * 5, key_prefix=PRODUCT_DETAIL_CACHE_PREFIX)
        def cached_get(request, prod_pk):
            product_qs = ProductRepository.get_all_active_products().annotate(
                individual_stock_qty=Subquery(
                    ProductStock.objects.filter(
                        product=OuterRef('pk'), status=True
                    ).values('quantity')[:1],
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
                    When(has_subproducts=False, individual_stock_qty__isnull=False, then=F('individual_stock_qty')),
                    When(has_subproducts=True, subproduct_stock_total__isnull=False, then=F('subproduct_stock_total')),
                    default=Decimal('0.00'),
                    output_field=DecimalField(max_digits=15, decimal_places=2)
                )
            )
            obj = get_object_or_404(product_qs, pk=prod_pk)
            ser = ProductSerializer(obj, context={'request': request})
            return Response(ser.data)

        return cached_get(request, prod_pk)

    # PUT → actualizar + stock
    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para actualizar este producto."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductSerializer(
            product, data=request.data, partial=True, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                updated = serializer.save(user=request.user)
                qty_change = serializer.validated_data.get('quantity_change')
                reason = serializer.validated_data.get('reason')
                if qty_change is not None:
                    if not updated.has_subproducts:
                        stock_rec = ProductStock.objects.select_for_update().get(product=updated)
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

        # Invalidar todas las páginas cacheadas
        delete_keys_by_pattern(f"{PRODUCT_LIST_CACHE_PREFIX}*")
        # Invalidar detalle cacheado
        cache.delete(cache_key_detail)

        return Response(ProductSerializer(updated, context={'request': request}).data)

    # DELETE → borrado suave
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para eliminar este producto."},
                status=status.HTTP_403_FORBIDDEN
            )

        product.delete(user=request.user)
        # Invalidar lista y detalle
        delete_keys_by_pattern(f"{PRODUCT_LIST_CACHE_PREFIX}*")
        cache.delete(cache_key_detail)

        return Response(status=status.HTTP_204_NO_CONTENT)
