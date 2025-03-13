from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.products.api.serializers.category_serializer import CategorySerializer

from apps.users.permissions import IsStaffOrReadOnly

from apps.core.pagination import Pagination

from apps.products.api.repositories.category_repository import CategoryRepository

from apps.products.docs.category_doc import (
    category_list_doc, create_category_doc, get_category_by_id_doc, update_category_by_id_doc,
    delete_category_by_id_doc
)

@extend_schema(**category_list_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def category_list(request):
    """
    Lista todas las categorías activas con paginación.
    """
    categories = CategoryRepository.get_all_active()  # Obtén todas las categorías activas
    paginator = Pagination()  # Paginador personalizado
    paginated_categories = paginator.paginate_queryset(categories, request)  # Paginamos el queryset
    serializer = CategorySerializer(paginated_categories, many=True)  # Serializamos los datos paginados
    return paginator.get_paginated_response(serializer.data)  # Respondemos con la paginación

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_category(request):
    """
    Crea una nueva categoría y asigna `created_by` al usuario autenticado.
    """
    user = request.user
    serializer = CategorySerializer(data=request.data, context={'request': request})  # Aquí pasamos el context

    if serializer.is_valid():
        # Crear la categoría usando el serializador
        category = serializer.save()
        return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_category_by_id_doc)
@extend_schema(**update_category_by_id_doc)
@extend_schema(**delete_category_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])  # Solo staff puede actualizar o eliminar; autenticados pueden leer.
def category_detail(request, category_pk):
    """
    Obtiene, actualiza o realiza un soft delete de una categoría específica.
    """
    category = CategoryRepository.get_by_id(category_pk)  # Usando el repositorio para obtener la categoría
    if not category:
        return Response({"detail": "Categoría no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Aseguramos que 'modified_by' sea el usuario autenticado al realizar la actualización
        serializer = CategorySerializer(category, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            # Pasa el usuario autenticado al serializador
            updated_category = CategoryRepository.update(category, **serializer.validated_data, user=request.user)
            return Response(CategorySerializer(updated_category).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user = request.user if request.user.is_authenticated else None
        if user:
            # Realizamos un soft delete usando el repositorio
            updated_category = CategoryRepository.soft_delete(category, user)
            return Response(
                {"detail": "Categoría eliminada (soft) correctamente."},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response({"detail": "No autorizado para eliminar esta categoría."}, status=status.HTTP_403_FORBIDDEN)