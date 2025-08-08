# apps/products/api/views/types_view.py

import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema

from apps.core.pagination import Pagination
from apps.products.api.serializers.type_serializer import TypeSerializer
from apps.products.api.repositories.type_repository import TypeRepository
from apps.products.filters.type_filter import TypeFilter
from apps.products.docs.type_doc import (
    list_type_doc,
    create_type_doc,
    get_type_by_id_doc,
    update_type_by_id_doc,
    delete_type_by_id_doc
)
from apps.products.utils.cache_helpers_types import CACHE_KEY_TYPE_LIST
from apps.products.utils.redis_utils import delete_keys_by_pattern

logger = logging.getLogger(__name__)

# ── CACHE DE LISTADO () ───────────────────────────────────
cache_decorator = (
    cache_page(None, key_prefix=CACHE_KEY_TYPE_LIST)
    if not settings.DEBUG
    else (lambda fn: fn)
)


@extend_schema(
    summary=list_type_doc["summary"],
    description=(
        list_type_doc["description"]
        + "\n\n⚠️ TTL=5min. Cambios recientes pueden tardar hasta 5min en verse."
    ),
    tags=list_type_doc["tags"],
    operation_id=list_type_doc["operation_id"],
    parameters=list_type_doc["parameters"],
    responses=list_type_doc["responses"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_decorator
def type_list(request):
    """
    Listar tipos con filtros y paginación.
    """
    queryset = TypeRepository.get_all_active()
    filtered_qs = TypeFilter(request.GET, queryset=queryset).qs

    paginator = Pagination()
    page = paginator.paginate_queryset(filtered_qs, request)
    data = TypeSerializer(page, many=True, context={'request': request}).data
    return paginator.get_paginated_response(data)


@extend_schema(
    summary=create_type_doc["summary"],
    description=create_type_doc["description"] + "\n\nInvalidará caché de lista.",
    tags=create_type_doc["tags"],
    operation_id=create_type_doc["operation_id"],
    request=create_type_doc["requestBody"],
    responses=create_type_doc["responses"],
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_type(request):
    """
    Crear un nuevo tipo (solo admins) e invalidar caché de lista.
    """
    serializer = TypeSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    instance = serializer.save(user=request.user)
    deleted = delete_keys_by_pattern(CACHE_KEY_TYPE_LIST)
    logger.debug(
        "Cache de type_list invalidada tras CREATE (borradas %d claves)",
        deleted
    )

    return Response(
        TypeSerializer(instance, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )


@extend_schema(
    summary=get_type_by_id_doc["summary"],
    description=get_type_by_id_doc["description"] + "\n\n⚠️ TTL=5min.",
    tags=get_type_by_id_doc["tags"],
    operation_id=get_type_by_id_doc["operation_id"],
    parameters=get_type_by_id_doc["parameters"],
    responses=get_type_by_id_doc["responses"],
)
@extend_schema(
    summary=update_type_by_id_doc["summary"],
    description=update_type_by_id_doc["description"] + "\n\nInvalidará caché de lista.",
    tags=update_type_by_id_doc["tags"],
    operation_id=update_type_by_id_doc["operation_id"],
    parameters=update_type_by_id_doc["parameters"],
    request=update_type_by_id_doc["requestBody"],
    responses=update_type_by_id_doc["responses"],
)
@extend_schema(
    summary=delete_type_by_id_doc["summary"],
    description=delete_type_by_id_doc["description"] + "\n\nInvalidará caché de lista.",
    tags=delete_type_by_id_doc["tags"],
    operation_id=delete_type_by_id_doc["operation_id"],
    parameters=delete_type_by_id_doc["parameters"],
    responses=delete_type_by_id_doc["responses"],
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def type_detail(request, type_pk):
    """
    GET: detalle (no cacheado).
    PUT: actualizar (solo admins) e invalidar caché de lista.
    DELETE: baja suave (solo admins) e invalidar caché de lista.
    """
    obj = TypeRepository.get_by_id(type_pk)
    if not obj:
        return Response({"detail": "Tipo no encontrado."},
                        status=status.HTTP_404_NOT_FOUND)

    # --- GET
    if request.method == 'GET':
        return Response(TypeSerializer(obj, context={'request': request}).data)

    # --- PUT
    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response({"detail": "Sin permiso."}, status=status.HTTP_403_FORBIDDEN)
        serializer = TypeSerializer(obj, data=request.data, context={'request': request}, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        updated = serializer.save(user=request.user)
        deleted = delete_keys_by_pattern(CACHE_KEY_TYPE_LIST)
        logger.debug(
            "Cache de type_list invalidada tras UPDATE (borradas %d claves)",
            deleted
        )
        return Response(TypeSerializer(updated, context={'request': request}).data)

    # --- DELETE
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({"detail": "Sin permiso."}, status=status.HTTP_403_FORBIDDEN)
        TypeRepository.soft_delete(obj, user=request.user)
        deleted = delete_keys_by_pattern(CACHE_KEY_TYPE_LIST)
        logger.debug(
            "Cache de type_list invalidada tras DELETE (borradas %d claves)",
            deleted
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
