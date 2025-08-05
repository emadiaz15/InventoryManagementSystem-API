# apps/products/api/views/products_view.py

import logging
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.core.pagination import Pagination
from apps.products.api.serializers.product_serializer import ProductSerializer
from apps.products.api.repositories.product_repository import ProductRepository
from apps.products.filters.product_filter import ProductFilter
from apps.products.docs.product_doc import (
    list_product_doc,
    create_product_doc,
    get_product_by_id_doc,
    update_product_by_id_doc,
    delete_product_by_id_doc
)

from apps.products.utils.cache_helpers_products import (
    PRODUCT_LIST_CACHE_PREFIX,
    PRODUCT_DETAIL_CACHE_PREFIX,
    product_detail_cache_key,
)
from apps.products.utils.redis_utils import delete_keys_by_pattern
from apps.stocks.models import ProductStock, SubproductStock
from apps.stocks.services import initialize_product_stock, adjust_product_stock

from django.db.models import Sum, F, Case, When, DecimalField, OuterRef, Subquery

logger = logging.getLogger(__name__)

# Decoradores condicionales
list_cache = (
    cache_page(60 * 15, key_prefix=PRODUCT_LIST_CACHE_PREFIX)
    if not settings.DEBUG
    else (lambda fn: fn)
)
detail_cache = (
    cache_page(60 *  5, key_prefix=PRODUCT_DETAIL_CACHE_PREFIX)
    if not settings.DEBUG
    else (lambda fn: fn)
)


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
@list_cache
def product_list(request):
    """
    Listar productos activos con paginación y stock calculado.
    """
    # construimos el queryset con subqueries de stock
    product_stock_sq = ProductStock.objects.filter(
        product=OuterRef('pk'), status=True
    ).values('quantity')[:1]
    subp_stock_sq = SubproductStock.objects.filter(
        subproduct__parent_id=OuterRef('pk'),
        status=True,
        subproduct__status=True
    ).values('subproduct__parent').annotate(
        total=Sum('quantity')
    ).values('total')

    qs = ProductRepository.get_all_active_products().annotate(
        individual_stock_qty=Subquery(product_stock_sq, output_field=DecimalField()),
        subproduct_stock_total=Subquery(subp_stock_sq, output_field=DecimalField())
    ).annotate(
        current_stock=Case(
            When(has_subproducts=False, individual_stock_qty__isnull=False, then=F('individual_stock_qty')),
            When(has_subproducts=True,  subproduct_stock_total__isnull=False, then=F('subproduct_stock_total')),
            default=Decimal('0.00'),
            output_field=DecimalField()
        )
    )

    # filtrado
    f = ProductFilter(request.GET, queryset=qs)
    if not f.is_valid():
        return Response(f.errors, status=status.HTTP_400_BAD_REQUEST)
    qs = f.qs

    # paginación
    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = ProductSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


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
    Crear un nuevo producto (solo admins), con opción de inicializar stock.
    """
    payload = request.data.copy()
    payload['has_subproducts'] = False

    # parsear initial_stock_quantity
    qty_str = payload.pop('initial_stock_quantity', '0')
    if isinstance(qty_str, list):
        qty_str = qty_str[0]
    reason = payload.pop('initial_stock_reason', 'Stock inicial por creación')

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

    serializer = ProductSerializer(data=payload, context={'request': request})
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

    # Invalidar caché de lista (todas las páginas y headers)
    delete_keys_by_pattern("views.decorators.cache.cache_page.product_list.GET.*")
    delete_keys_by_pattern("views.decorators.cache.cache_header.product_list.*")
    logger.debug("[Cache] Cache_product_list invalidada (pattern aplicado)")

    return Response(
        ProductSerializer(product, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )


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
    """
    GET: detalle cacheado
    PUT: actualizar + stock
    DELETE: baja suave
    """
    product = ProductRepository.get_by_id(prod_pk)
    if not product:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # GENERAR cache key de detalle
    detail_key = product_detail_cache_key(prod_pk)

    if request.method == 'GET':
        @detail_cache
        def cached_get(req, pk):
            obj = get_object_or_404(
                ProductRepository.get_all_active_products(), pk=pk
            )
            ser = ProductSerializer(obj, context={'request': req})
            return Response(ser.data)

        return cached_get(request, prod_pk)

    # PUT → actualización
    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response({"detail": "Permiso denegado."}, status=status.HTTP_403_FORBIDDEN)

        ser = ProductSerializer(
            product, data=request.data, partial=True, context={'request': request}
        )
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                updated = ser.save(user=request.user)
                qty_change = ser.validated_data.get('quantity_change')
                reason     = ser.validated_data.get('reason')
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
            code   = status.HTTP_400_BAD_REQUEST if isinstance(e, (serializers.ValidationError, ValidationError)) else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response({"detail": detail}, status=code)

        # Invalidar caché de lista y detalle
        delete_keys_by_pattern("views.decorators.cache.cache_page.product_list.GET.*")
        delete_keys_by_pattern("views.decorators.cache.cache_header.product_list.*")
        delete_keys_by_pattern("views.decorators.cache.cache_page.product_detail.GET.*")
        delete_keys_by_pattern("views.decorators.cache.cache_header.product_detail.*")
        logger.debug(f"[Cache] Cache_product_list y Cache_product_detail invalidadas tras UPDATE")

        return Response(ProductSerializer(updated, context={'request': request}).data)

    # DELETE → baja suave
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({"detail": "Permiso denegado."}, status=status.HTTP_403_FORBIDDEN)

        product.delete(user=request.user)

        # Invalidar caché de lista y detalle
        delete_keys_by_pattern("views.decorators.cache.cache_page.product_list.GET.*")
        delete_keys_by_pattern("views.decorators.cache.cache_header.product_list.*")
        delete_keys_by_pattern("views.decorators.cache.cache_page.product_detail.GET.*")
        delete_keys_by_pattern("views.decorators.cache.cache_header.product_detail.*")
        logger.debug(f"[Cache] Cache_product_list y Cache_product_detail invalidadas tras DELETE")

        return Response(status=status.HTTP_204_NO_CONTENT)
