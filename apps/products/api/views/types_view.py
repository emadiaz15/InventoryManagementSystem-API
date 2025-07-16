from django.core.cache import cache
from django_redis import get_redis_connection
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

CACHE_KEY_TYPE_LIST = "type_list"

# --- Listar tipos activos con filtros y paginación ---
@extend_schema(
    summary=list_type_doc["summary"],
    description=list_type_doc["description"] + "\n\n⚠️ Nota: Este endpoint puede entregar datos cacheados durante un breve período (TTL: 5 minutos). Los cambios recientes pueden no reflejarse de inmediato.",
    tags=list_type_doc["tags"],
    operation_id=list_type_doc["operation_id"],
    parameters=list_type_doc["parameters"],
    responses=list_type_doc["responses"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60 * 5, key_prefix=CACHE_KEY_TYPE_LIST)
def type_list(request):
    """
    Endpoint para listar los tipos activos, con filtros por nombre y paginación.
    """
    queryset = TypeRepository.get_all_active()
    filterset = TypeFilter(request.GET, queryset=queryset)
    qs = filterset.qs

    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = TypeSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# --- Crear nuevo tipo de producto (solo admins) ---
@extend_schema(
    summary=create_type_doc["summary"],
    description=create_type_doc["description"] + "\n\nEsta acción invalidará automáticamente la cache de tipos.",
    tags=create_type_doc["tags"],
    operation_id=create_type_doc["operation_id"],
    request=create_type_doc["requestBody"],
    responses=create_type_doc["responses"]
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_type(request):
    """
    Endpoint para crear un nuevo tipo de producto.
    Solo administradores.
    """
    serializer = TypeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        type_instance = serializer.save(user=request.user)
        # invalida todas las cachés de lista de tipos
        redis_client = get_redis_connection("default")
        redis_client.delete_pattern(f"{CACHE_KEY_TYPE_LIST}*")
        return Response(
            TypeSerializer(type_instance, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- Obtener, actualizar y eliminar tipo por ID ---
@extend_schema(
    summary=get_type_by_id_doc["summary"],
    description=get_type_by_id_doc["description"] + "\n\n⚠️ Nota: Este endpoint puede entregar datos cacheados durante 5 minutos. Los cambios recientes pueden no reflejarse de inmediato.",
    tags=get_type_by_id_doc["tags"],
    operation_id=get_type_by_id_doc["operation_id"],
    parameters=get_type_by_id_doc["parameters"],
    responses=get_type_by_id_doc["responses"]
)
@extend_schema(
    summary=update_type_by_id_doc["summary"],
    description=update_type_by_id_doc["description"] + "\n\nEsta acción invalidará automáticamente la cache relacionada a los tipos.",
    tags=update_type_by_id_doc["tags"],
    operation_id=update_type_by_id_doc["operation_id"],
    parameters=update_type_by_id_doc["parameters"],
    request=update_type_by_id_doc["requestBody"],
    responses=update_type_by_id_doc["responses"]
)
@extend_schema(
    summary=delete_type_by_id_doc["summary"],
    description=delete_type_by_id_doc["description"] + "\n\nEsta acción invalidará automáticamente la cache de tipos.",
    tags=delete_type_by_id_doc["tags"],
    operation_id=delete_type_by_id_doc["operation_id"],
    parameters=delete_type_by_id_doc["parameters"],
    responses=delete_type_by_id_doc["responses"]
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def type_detail(request, type_pk):
    """
    Endpoint para:
    - GET: consultar detalles de un tipo.
    - PUT: actualizar tipo (solo administradores).
    - DELETE: eliminar tipo de forma suave (solo administradores).
    """
    type_instance = TypeRepository.get_by_id(type_pk)
    if not type_instance:
        return Response({"detail": "Tipo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TypeSerializer(type_instance, context={'request': request})
        return Response(serializer.data)

    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response({"detail": "No tienes permiso para actualizar este tipo."}, status=status.HTTP_403_FORBIDDEN)

        serializer = TypeSerializer(type_instance, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            updated = serializer.save(user=request.user)
            # invalida todas las cachés de lista de tipos
            redis_client = get_redis_connection("default")
            redis_client.delete_pattern(f"{CACHE_KEY_TYPE_LIST}*")
            return Response(TypeSerializer(updated, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({"detail": "No tienes permiso para eliminar este tipo."}, status=status.HTTP_403_FORBIDDEN)

        serializer = TypeSerializer(type_instance, data={'status': False}, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            # invalida todas las cachés de lista de tipos
            redis_client = get_redis_connection("default")
            redis_client.delete_pattern(f"{CACHE_KEY_TYPE_LIST}*")
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
