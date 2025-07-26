# apps/products/api/views/category_view.py

import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.products.utils.cache_helpers_categories import (
    CACHE_KEY_CATEGORY_LIST,
    category_list_cache_key,
)

# Primero importamos CACHE_KEY_CATEGORY_LIST, luego creamos el decorador condicional
from django.views.decorators.cache import cache_page
cache_decorator = (
    cache_page(60 * 5, key_prefix=CACHE_KEY_CATEGORY_LIST)
    if not settings.DEBUG
    else (lambda fn: fn)
)

from apps.core.pagination import Pagination
from apps.products.models.category_model import Category
from apps.products.api.serializers.category_serializer import CategorySerializer
from apps.products.api.repositories.category_repository import CategoryRepository
from apps.products.filters.category_filter import CategoryFilter
from apps.products.docs.category_doc import (
    list_category_doc,
    create_category_doc,
    get_category_by_id_doc,
    update_category_by_id_doc,
    delete_category_by_id_doc,
)

logger = logging.getLogger(__name__)


@extend_schema(
    summary=list_category_doc["summary"],
    description=(
        list_category_doc["description"]
        + "\n\n⚠️ Nota: Este endpoint puede entregar datos cacheados durante un breve período (TTL: 5 minutos). "
        "Los cambios recientes pueden no reflejarse de inmediato."
    ),
    tags=list_category_doc["tags"],
    operation_id=list_category_doc["operation_id"],
    parameters=list_category_doc["parameters"],
    responses=list_category_doc["responses"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_decorator
def category_list(request):
    """
    Endpoint para listar las categorías activas, con filtros por nombre y paginación.
    """
    queryset = Category.objects.filter(status=True).select_related('created_by')
    filtered_qs = CategoryFilter(request.GET, queryset=queryset).qs

    paginator = Pagination()
    page = paginator.paginate_queryset(filtered_qs, request)
    serializer = CategorySerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(
    summary=create_category_doc["summary"],
    description=(
        create_category_doc["description"]
        + "\n\nEsta acción invalidará la caché de la página 1 de categorías."
    ),
    tags=create_category_doc["tags"],
    operation_id=create_category_doc["operation_id"],
    request=create_category_doc["requestBody"],
    responses=create_category_doc["responses"],
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_category(request):
    """
    Endpoint para crear una nueva categoría (solo admins).
    """
    serializer = CategorySerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    category = serializer.save(user=request.user)

    # Invalidar únicamente la página 1 de la lista cacheada
    page_size = int(request.GET.get('page_size', 10))
    name_filter = request.GET.get('name', '')
    cache_key = category_list_cache_key(page=1, page_size=page_size, name=name_filter)
    cache.delete(cache_key)
    logger.debug(f"[Cache] Deleted key: {cache_key}")

    return Response(
        CategorySerializer(category, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )


@extend_schema(
    summary=get_category_by_id_doc["summary"],
    description=(
        get_category_by_id_doc["description"]
        + "\n\n⚠️ Nota: Este endpoint puede entregar datos cacheados durante 5 minutos."
    ),
    tags=get_category_by_id_doc["tags"],
    operation_id=get_category_by_id_doc["operation_id"],
    parameters=get_category_by_id_doc["parameters"],
    responses=get_category_by_id_doc["responses"],
)
@extend_schema(
    summary=update_category_by_id_doc["summary"],
    description=(
        update_category_by_id_doc["description"]
        + "\n\nEsta acción invalidará la caché de la página 1 de categorías."
    ),
    tags=update_category_by_id_doc["tags"],
    operation_id=update_category_by_id_doc["operation_id"],
    parameters=update_category_by_id_doc["parameters"],
    request=update_category_by_id_doc["requestBody"],
    responses=update_category_by_id_doc["responses"],
)
@extend_schema(
    summary=delete_category_by_id_doc["summary"],
    description=(
        delete_category_by_id_doc["description"]
        + "\n\nEsta acción invalidará la caché de la página 1 de categorías."
    ),
    tags=delete_category_by_id_doc["tags"],
    operation_id=delete_category_by_id_doc["operation_id"],
    parameters=delete_category_by_id_doc["parameters"],
    responses=delete_category_by_id_doc["responses"],
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def category_detail(request, category_pk):
    """
    GET: Detalle de categoría.
    PUT: Actualiza categoría (solo admins).
    DELETE: Soft-delete categoría (solo admins).
    """
    category = CategoryRepository.get_by_id(category_pk)
    if not category:
        return Response({"detail": "Categoría no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    # Parámetros para invalidar la caché
    page_size = int(request.GET.get('page_size', 10))
    name_filter = request.GET.get('name', '')

    # --- GET ---
    if request.method == 'GET':
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)

    # --- PUT ---
    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para actualizar esta categoría."},
                status=status.HTTP_403_FORBIDDEN
            )
        ser = CategorySerializer(
            category,
            data=request.data,
            context={'request': request},
            partial=True
        )
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        updated = CategoryRepository.update(
            category_instance=category,
            user=request.user,
            name=ser.validated_data.get('name'),
            description=ser.validated_data.get('description')
        )

        cache_key = category_list_cache_key(page=1, page_size=page_size, name=name_filter)
        cache.delete(cache_key)
        logger.debug(f"[Cache] Deleted key: {cache_key}")

        return Response(CategorySerializer(updated, context={'request': request}).data)

    # --- DELETE ---
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para eliminar esta categoría."},
                status=status.HTTP_403_FORBIDDEN
            )

        CategoryRepository.soft_delete(category, user=request.user)

        cache_key = category_list_cache_key(page=1, page_size=page_size, name=name_filter)
        cache.delete(cache_key)
        logger.debug(f"[Cache] Deleted key: {cache_key}")

        return Response(status=status.HTTP_204_NO_CONTENT)
