from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema

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
    delete_category_by_id_doc
)
from apps.products.utils.redis_utils import delete_keys_by_pattern

CACHE_KEY_CATEGORY_LIST = "category_list"

# --- Obtener categorías activas con filtros y paginación ---
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
    responses=list_category_doc["responses"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60 * 5, key_prefix=CACHE_KEY_CATEGORY_LIST)
def category_list(request):
    """
    Endpoint para listar las categorías activas, con filtros por nombre y paginación.
    """
    queryset = Category.objects.filter(status=True).select_related('created_by')
    filterset = CategoryFilter(request.GET, queryset=queryset)
    qs = filterset.qs

    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = CategorySerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# --- Crear nueva categoría (solo admins) ---
@extend_schema(
    summary=create_category_doc["summary"],
    description=(
        create_category_doc["description"]
        + "\n\nEsta acción invalidará automáticamente la cache de categorías."
    ),
    tags=create_category_doc["tags"],
    operation_id=create_category_doc["operation_id"],
    request=create_category_doc["requestBody"],
    responses=create_category_doc["responses"]
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_category(request):
    """
    Endpoint para crear una nueva categoría.
    Solo accesible para administradores.
    """
    serializer = CategorySerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        category = serializer.save(user=request.user)
        # invalida todas las cachés de lista de categorías
        delete_keys_by_pattern(f"{CACHE_KEY_CATEGORY_LIST}*")
        return Response(
            CategorySerializer(category, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- Obtener, actualizar y eliminar categoría por ID ---
@extend_schema(
    summary=get_category_by_id_doc["summary"],
    description=(
        get_category_by_id_doc["description"]
        + "\n\n⚠️ Nota: Este endpoint puede entregar datos cacheados durante 5 minutos. "
        "Los cambios recientes pueden no reflejarse de inmediato."
    ),
    tags=get_category_by_id_doc["tags"],
    operation_id=get_category_by_id_doc["operation_id"],
    parameters=get_category_by_id_doc["parameters"],
    responses=get_category_by_id_doc["responses"]
)
@extend_schema(
    summary=update_category_by_id_doc["summary"],
    description=(
        update_category_by_id_doc["description"]
        + "\n\nEsta acción invalidará automáticamente la cache relacionada a la categoría."
    ),
    tags=update_category_by_id_doc["tags"],
    operation_id=update_category_by_id_doc["operation_id"],
    parameters=update_category_by_id_doc["parameters"],
    request=update_category_by_id_doc["requestBody"],
    responses=update_category_by_id_doc["responses"]
)
@extend_schema(
    summary=delete_category_by_id_doc["summary"],
    description=(
        delete_category_by_id_doc["description"]
        + "\n\nEsta acción invalidará automáticamente la cache de categorías."
    ),
    tags=delete_category_by_id_doc["tags"],
    operation_id=delete_category_by_id_doc["operation_id"],
    parameters=delete_category_by_id_doc["parameters"],
    responses=delete_category_by_id_doc["responses"]
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def category_detail(request, category_pk):
    """
    Endpoint para:
    - GET: consultar detalles de una categoría.
    - PUT: actualizar categoría (solo administradores).
    - DELETE: eliminar categoría de forma suave (solo administradores).
    """
    category = CategoryRepository.get_by_id(category_pk)
    if not category:
        return Response({"detail": "Categoría no encontrada."}, status=status.HTTP_404_NOT_FOUND)

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
        serializer = CategorySerializer(
            category,
            data=request.data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            updated_category = CategoryRepository.update(
                category_instance=category,
                user=request.user,
                name=serializer.validated_data.get('name'),
                description=serializer.validated_data.get('description')
            )
            # invalida todas las cachés de lista de categorías
            delete_keys_by_pattern(f"{CACHE_KEY_CATEGORY_LIST}*")
            return Response(
                CategorySerializer(updated_category, context={'request': request}).data
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- DELETE ---
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para eliminar esta categoría."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CategorySerializer(
            category,
            data={'status': False},
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save(user=request.user)
            # invalida todas las cachés de lista de categorías
            delete_keys_by_pattern(f"{CACHE_KEY_CATEGORY_LIST}*")
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
