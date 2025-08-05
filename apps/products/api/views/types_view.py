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
from apps.products.utils.cache_helpers_types import (
    CACHE_KEY_TYPE_LIST
)
from apps.products.utils.redis_utils import delete_keys_by_pattern

logger = logging.getLogger(__name__)

# aplicamos cache_page solo si NO estamos en DEBUG
cache_decorator = (
    cache_page(60 * 5, key_prefix=CACHE_KEY_TYPE_LIST)
    if not settings.DEBUG
    else (lambda fn: fn)
)

@extend_schema(
    summary=list_type_doc["summary"],
    description=(
        list_type_doc["description"]
        + "\n\n⚠️ Nota: Este endpoint puede entregar datos cacheados durante un breve período (TTL: 5 minutos). "
        "Los cambios recientes pueden no reflejarse de inmediato."
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
    Listar tipos activos, con filtros por nombre y paginación.
    """
    queryset = TypeRepository.get_all_active()
    filtered_qs = TypeFilter(request.GET, queryset=queryset).qs

    paginator = Pagination()
    page = paginator.paginate_queryset(filtered_qs, request)
    serializer = TypeSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

@extend_schema(
    summary=create_type_doc["summary"],
    description=(
        create_type_doc["description"]
        + "\n\nEsta acción invalidará la caché de la lista de tipos."
    ),
    tags=create_type_doc["tags"],
    operation_id=create_type_doc["operation_id"],
    request=create_type_doc["requestBody"],
    responses=create_type_doc["responses"],
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_type(request):
    """
    Crear un nuevo tipo de producto (solo admins).
    """
    serializer = TypeSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    type_instance = serializer.save(user=request.user)

    # Invalidar caché de lista de tipos (body y headers)
    delete_keys_by_pattern("views.decorators.cache.cache_page.type_list.GET.*")
    delete_keys_by_pattern("views.decorators.cache.cache_header.type_list.*")
    logger.debug("[Cache] Cache_type_list invalidada (pattern aplicado)")

    return Response(
        TypeSerializer(type_instance, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )

@extend_schema(
    summary=get_type_by_id_doc["summary"],
    description=(
        get_type_by_id_doc["description"]
        + "\n\n⚠️ Nota: Este endpoint puede entregar datos cacheados durante 5 minutos."
    ),
    tags=get_type_by_id_doc["tags"],
    operation_id=get_type_by_id_doc["operation_id"],
    parameters=get_type_by_id_doc["parameters"],
    responses=get_type_by_id_doc["responses"],
)
@extend_schema(
    summary=update_type_by_id_doc["summary"],
    description=(
        update_type_by_id_doc["description"]
        + "\n\nEsta acción invalidará la caché de la lista de tipos."
    ),
    tags=update_type_by_id_doc["tags"],
    operation_id=update_type_by_id_doc["operation_id"],
    parameters=update_type_by_id_doc["parameters"],
    request=update_type_by_id_doc["requestBody"],
    responses=update_type_by_id_doc["responses"],
)
@extend_schema(
    summary=delete_type_by_id_doc["summary"],
    description=(
        delete_type_by_id_doc["description"]
        + "\n\nEsta acción invalidará la caché de la lista de tipos."
    ),
    tags=delete_type_by_id_doc["tags"],
    operation_id=delete_type_by_id_doc["operation_id"],
    parameters=delete_type_by_id_doc["parameters"],
    responses=delete_type_by_id_doc["responses"],
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def type_detail(request, type_pk):
    """
    GET: detalle de tipo.
    PUT: actualizar tipo (solo admins).
    DELETE: baja suave del tipo (solo admins).
    """
    type_instance = TypeRepository.get_by_id(type_pk)
    if not type_instance:
        return Response({"detail": "Tipo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # --- GET ---
    if request.method == 'GET':
        serializer = TypeSerializer(type_instance, context={'request': request})
        return Response(serializer.data)

    # --- PUT ---
    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para actualizar este tipo."},
                status=status.HTTP_403_FORBIDDEN
            )
        ser = TypeSerializer(
            type_instance,
            data=request.data,
            context={'request': request},
            partial=True
        )
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        updated = ser.save(user=request.user)

        # Invalidar caché de lista de tipos
        delete_keys_by_pattern("views.decorators.cache.cache_page.type_list.GET.*")
        delete_keys_by_pattern("views.decorators.cache.cache_header.type_list.*")
        logger.debug("[Cache] Cache_type_list invalidada tras UPDATE")

        return Response(TypeSerializer(updated, context={'request': request}).data)

    # --- DELETE ---
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para eliminar este tipo."},
                status=status.HTTP_403_FORBIDDEN
            )
        updated = TypeRepository.soft_delete(type_instance, user=request.user)

        # Invalidar caché de lista de tipos
        delete_keys_by_pattern("views.decorators.cache.cache_page.type_list.GET.*")
        delete_keys_by_pattern("views.decorators.cache.cache_header.type_list.*")
        logger.debug("[Cache] Cache_type_list invalidada tras DELETE")

        return Response(status=status.HTTP_204_NO_CONTENT)
