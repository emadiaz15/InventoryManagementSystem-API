from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.users.permissions import IsStaffOrReadOnly

from apps.core.pagination import Pagination

from apps.products.api.serializers.type_serializer import TypeSerializer

from apps.products.api.repositories.type_repository import TypeRepository

from apps.products.docs.type_doc import (
    list_type_doc, create_type_doc, get_type_by_id_doc, update_type_by_id_doc,
    delete_type_by_id_doc
)

@extend_schema(**list_type_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def type_list(request):
    """
    Lista todos los tipos activos con paginación.
    """
    types = TypeRepository.get_all_active()  # Obtén todos los tipos activos
    paginator = Pagination()  # Paginador personalizado
    paginated_types = paginator.paginate_queryset(types, request)  # Paginamos el queryset
    serializer = TypeSerializer(paginated_types, many=True)  # Serializamos los datos paginados
    return paginator.get_paginated_response(serializer.data)  # Respondemos con la paginación

@extend_schema(**create_type_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])  # Solo el staff puede crear
def create_type(request):
    """
    Crea un nuevo tipo de producto.
    """
    # Aseguramos que el request tiene un 'user' autenticado
    if not request.user.is_authenticated:
        return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = TypeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        # Crear el tipo de producto usando el serializador
        type_instance = serializer.save()
        return Response(TypeSerializer(type_instance).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_type_by_id_doc)
@extend_schema(**update_type_by_id_doc)
@extend_schema(**delete_type_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])  # Solo staff puede actualizar o eliminar; autenticados pueden leer
def type_detail(request, type_pk):
    """
    Obtiene, actualiza o realiza un soft delete de un tipo específico.
    """
    type_instance = TypeRepository.get_by_id(type_pk)  # Usando el repositorio para obtener el tipo
    if not type_instance:
        return Response({"detail": "Tipo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Obtenemos el tipo y lo serializamos
        serializer = TypeSerializer(type_instance)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Aseguramos que 'modified_by' sea el usuario autenticado al realizar la actualización
        serializer = TypeSerializer(type_instance, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            # Pasa el usuario autenticado al serializador para realizar la actualización
            updated_type = TypeRepository.update(type_instance, **serializer.validated_data, user=request.user)
            return Response(TypeSerializer(updated_type).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Solo el usuario autenticado puede eliminar
        user = request.user if request.user.is_authenticated else None
        if user:
            # Realizamos un soft delete usando el repositorio
            updated_type = TypeRepository.soft_delete(type_instance, user)
            return Response(
                {"detail": "Tipo eliminado (soft) correctamente."},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response({"detail": "No autorizado para eliminar este tipo."}, status=status.HTTP_403_FORBIDDEN)
