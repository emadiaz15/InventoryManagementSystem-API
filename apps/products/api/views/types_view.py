from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema

from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination
from apps.products.api.serializers.type_serializer import TypeSerializer
from apps.products.api.repositories.type_repository import TypeRepository
from apps.products.docs.type_doc import (
    list_type_doc, create_type_doc, get_type_by_id_doc, update_type_by_id_doc,
    delete_type_by_id_doc
)
from apps.products.filters.type_filter import TypeFilter

@extend_schema(**list_type_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def type_list(request):
    """
    Lista todos los tipos activos con paginación y filtros.
    Permite filtrar por nombre del tipo y por nombre de la categoría asociada.
    """
    # 1. Obtener el queryset base de tipos activos.
    queryset = TypeRepository.get_all_active()

    # 2. Aplicar filtros mediante TypeFilter utilizando los parámetros enviados en la request.
    filterset = TypeFilter(request.GET, queryset=queryset)
    filtered_queryset = filterset.qs

    # 3. Paginación
    paginator = Pagination()
    paginated_types = paginator.paginate_queryset(filtered_queryset, request)

    # 4. Serialización (con contexto)
    serializer = TypeSerializer(paginated_types, many=True, context={'request': request})
    
    # 5. Respuesta
    return paginator.get_paginated_response(serializer.data)

@extend_schema(**create_type_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_type(request):
    """Crea un nuevo tipo de producto."""
    serializer = TypeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        # Correcto: Usa serializer.save() pasando el user
        type_instance = serializer.save(user=request.user)
        return Response(TypeSerializer(type_instance, context={'request': request}).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(**get_type_by_id_doc)
@extend_schema(**update_type_by_id_doc)
@extend_schema(**delete_type_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def type_detail(request, type_pk):
    """Obtiene, actualiza o realiza un soft delete de un tipo específico."""
    type_instance = TypeRepository.get_by_id(type_pk)
    if not type_instance:
        return Response({"detail": "Tipo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TypeSerializer(type_instance, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TypeSerializer(type_instance, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            # Correcto: Usa serializer.save() pasando el user
            updated_type = serializer.save(user=request.user)
            return Response(TypeSerializer(updated_type, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Correcto: Usa el repositorio que ahora llama a instance.delete() correctamente
        TypeRepository.soft_delete(type_instance, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
        # Alternativa (también correcta) sería usar el serializer como en Category:
        # serializer = TypeSerializer(type_instance, data={'status': False}, context={'request': request}, partial=True)
        # if serializer.is_valid():
        #     serializer.save(user=request.user)
        #     return Response(status=status.HTTP_204_NO_CONTENT)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
