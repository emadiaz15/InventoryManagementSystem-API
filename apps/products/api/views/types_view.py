from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.utils import timezone # Import timezone

from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination
from apps.products.api.serializers.type_serializer import TypeSerializer
from apps.products.api.repositories.type_repository import TypeRepository 
# Importaciones de Docs
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
    types = TypeRepository.get_all_active()
    paginator = Pagination()
    paginated_types = paginator.paginate_queryset(types, request)
    serializer = TypeSerializer(paginated_types, many=True, context={'request': request}) # Pasar contexto es buena práctica
    return paginator.get_paginated_response(serializer.data)

@extend_schema(**create_type_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_type(request):
    """
    Crea un nuevo tipo de producto.
    """
    if not request.user.is_authenticated:
        return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

    serializer = TypeSerializer(data=request.data, context={'request': request}) # Pasa el contexto

    if serializer.is_valid():
        # Usa serializer.save() que llama a serializer.create()
        # Pasa el usuario al método save para que lo use internamente
        type_instance = serializer.save(user=request.user) # Pasar user aquí
        # Devuelve los datos serializados del objeto creado
        return Response(TypeSerializer(type_instance, context={'request': request}).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(**get_type_by_id_doc)
@extend_schema(**update_type_by_id_doc)
@extend_schema(**delete_type_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def type_detail(request, type_pk):
    """
    Obtiene, actualiza o realiza un soft delete de un tipo específico.
    """
    type_instance = TypeRepository.get_by_id(type_pk)
    if not type_instance:
        return Response({"detail": "Tipo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TypeSerializer(type_instance, context={'request': request}) # Pasa contexto
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Usamos el serializer para validar y actualizar
        # Pasamos partial=True por si no se envían todos los campos (aunque PUT usualmente espera todos)
        serializer = TypeSerializer(type_instance, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            # --- ¡CAMBIO CLAVE AQUÍ! ---
            # Usamos serializer.save() en lugar de TypeRepository.update
            # Pasamos el usuario para que el serializer lo use en su método update
            updated_type = serializer.save(user=request.user)
            # Devolvemos la instancia actualizada y serializada
            return Response(TypeSerializer(updated_type, context={'request': request}).data)
            # --- FIN DEL CAMBIO ---
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # La lógica de soft delete puede quedarse en el repositorio o moverse al modelo/serializer
        # Manteniendo la llamada al repositorio por ahora:
        user = request.user if request.user.is_authenticated else None
        if user:
            # Llamamos al método específico de soft_delete del repositorio
            # Podrías considerar mover esta lógica al método delete del Modelo si prefieres
            TypeRepository.soft_delete(type_instance, user)
            return Response(status=status.HTTP_204_NO_CONTENT) # Éxito sin contenido
        else:
            return Response({"detail": "No autorizado para eliminar este tipo."}, status=status.HTTP_403_FORBIDDEN)