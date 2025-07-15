from django.core.cache import cache
from decimal import Decimal, InvalidOperation
import logging

from django.db import transaction
from django.db.models import OuterRef, Subquery, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.cache import cache_page
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.core.pagination import Pagination
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.api.repositories.subproduct_repository import SubproductRepository
from apps.products.filters.subproduct_filter import SubproductFilter
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

from django_redis import get_redis_connection
from apps.products.utils.cache_helpers import (
    SUBPRODUCT_LIST_CACHE_PREFIX,
    SUBPRODUCT_DETAIL_CACHE_PREFIX,
    subproduct_list_cache_key,
    subproduct_detail_cache_key,
)

logger = logging.getLogger(__name__)

# --- Listar subproductos activos de un producto ---
@extend_schema(
    summary=list_subproducts_doc["summary"], 
    description=list_subproducts_doc["description"],
    tags=list_subproducts_doc["tags"],
    operation_id=list_subproducts_doc["operation_id"],
    parameters=list_subproducts_doc["parameters"],
    responses=list_subproducts_doc["responses"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60 * 15, key_prefix=SUBPRODUCT_LIST_CACHE_PREFIX)
def subproduct_list(request, prod_pk):
    """
    Endpoint para listar subproductos de un producto padre,
    filtrables por status, con paginación e incluyendo el stock actual.
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

    filterset = SubproductFilter(request.GET, queryset=qs)
    if not filterset.is_valid():
        return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
    qs = filterset.qs

    paginator = Pagination()
    paginator.page_size = 10
    page = paginator.paginate_queryset(qs, request)
    serializer = SubProductSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# --- Crear nuevo subproducto ---
@extend_schema(
    summary=create_subproduct_doc["summary"], 
    description=create_subproduct_doc["description"],
    tags=create_subproduct_doc["tags"],
    operation_id=create_subproduct_doc["operation_id"],
    request=create_subproduct_doc["request"], 
    responses=create_subproduct_doc["responses"]
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_subproduct(request, prod_pk):
    """
    Crea un nuevo subproducto asignándole el producto padre.
    """
    parent = get_object_or_404(Product, pk=prod_pk, status=True)

    serializer = SubProductSerializer(
        data=request.data,
        context={'request': request, 'parent_product': parent}
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            subp = serializer.save(user=request.user)
    except serializers.ValidationError as e:
        return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 1) Invalido todas las cachés de lista de subproductos
    redis = get_redis_connection()
    redis.delete_pattern(f"{SUBPRODUCT_LIST_CACHE_PREFIX}*")
    # 2) (Opcional) Invalido la caché de detalle de este subproducto recién creado
    cache.delete(subproduct_detail_cache_key(prod_pk, subp.pk))

    resp_ser = SubProductSerializer(
        subp,
        context={'request': request, 'parent_product': parent}
    )
    return Response(resp_ser.data, status=status.HTTP_201_CREATED)


# --- Obtener, actualizar y eliminar subproducto por ID ---
@extend_schema(
    summary=get_subproduct_by_id_doc["summary"],
    description=get_subproduct_by_id_doc["description"],
    tags=get_subproduct_by_id_doc["tags"],
    operation_id=get_subproduct_by_id_doc["operation_id"],
    parameters=get_subproduct_by_id_doc["parameters"],
    responses=get_subproduct_by_id_doc["responses"]
)
@extend_schema(
    summary=update_subproduct_by_id_doc["summary"],
    description=update_subproduct_by_id_doc["description"],
    tags=update_subproduct_by_id_doc["tags"],
    operation_id=update_subproduct_by_id_doc["operation_id"],
    parameters=update_subproduct_by_id_doc["parameters"],
    request=create_subproduct_doc["request"], 
    responses=update_subproduct_by_id_doc["responses"]
)
@extend_schema(
    summary=delete_subproduct_by_id_doc["summary"],
    description=delete_subproduct_by_id_doc["description"],
    tags=delete_subproduct_by_id_doc["tags"],
    operation_id=delete_subproduct_by_id_doc["operation_id"],
    parameters=delete_subproduct_by_id_doc["parameters"],
    responses=delete_subproduct_by_id_doc["responses"]
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def subproduct_detail(request, prod_pk, subp_pk):
    """
    Endpoint para:
    - GET: consulta (cacheada).
    - PUT: actualización (solo staff).
    - DELETE: baja suave (solo staff).
    """
    parent = get_object_or_404(Product, pk=prod_pk, status=True)
    cache_key_detail = subproduct_detail_cache_key(prod_pk, subp_pk)

    if request.method == 'GET':
        @cache_page(60 * 5, key_prefix=SUBPRODUCT_DETAIL_CACHE_PREFIX)
        def cached_get(request, prod_pk, subp_pk):
            stock_sq = SubproductStock.objects.filter(subproduct=OuterRef('pk'), status=True).values('quantity')[:1]
            qs = Subproduct.objects.annotate(
                current_stock_val=Subquery(stock_sq, output_field=DecimalField(max_digits=15, decimal_places=2))
            ).annotate(
                current_stock=Coalesce('current_stock_val', Decimal('0.00'), output_field=DecimalField(max_digits=15, decimal_places=2))
            )
            instance = get_object_or_404(qs, pk=subp_pk, parent=parent)
            ser = SubProductSerializer(instance, context={'request': request, 'parent_product': parent})
            return Response(ser.data)

        return cached_get(request, prod_pk, subp_pk)

    instance = get_object_or_404(Subproduct, pk=subp_pk, parent=parent, status=True)

    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response({"detail": "No tienes permiso para actualizar este subproducto."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SubProductSerializer(instance, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                updated = serializer.save(user=request.user)
                qty_change = serializer.validated_data.get('quantity_change')
                reason = serializer.validated_data.get('reason')
                if qty_change is not None:
                    stock_rec = SubproductStock.objects.select_for_update().get(subproduct=updated, status=True)
                    adjust_subproduct_stock(
                        subproduct_stock=stock_rec,
                        quantity_change=qty_change,
                        reason=reason,
                        user=request.user
                    )
        except Exception as e:
            logger.error(f"Error actualizando subproducto {subp_pk}: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Invalido todas las cachés de lista de subproductos
        redis = get_redis_connection()
        redis.delete_pattern(f"{SUBPRODUCT_LIST_CACHE_PREFIX}*")
        # Invalido caché de detalle concreto
        cache.delete(cache_key_detail)

        resp_ser = SubProductSerializer(updated, context={'request': request, 'parent_product': parent})
        return Response(resp_ser.data)

    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({"detail": "No tienes permiso para eliminar este subproducto."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            instance.delete(user=request.user)
        except Exception as e:
            logger.error(f"Error eliminando subproducto {subp_pk}: {e}")
            return Response({"detail": "Error interno al eliminar el subproducto."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
       # Invalido todas las cachés de lista de subproductos
        redis = get_redis_connection()
        redis.delete_pattern(f"{SUBPRODUCT_LIST_CACHE_PREFIX}*")
        # Invalido caché de detalle concreto
        cache.delete(cache_key_detail)

        return Response(status=status.HTTP_204_NO_CONTENT)
