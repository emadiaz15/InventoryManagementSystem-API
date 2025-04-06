from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema

from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination
from apps.products.api.serializers.category_serializer import CategorySerializer
from apps.products.api.repositories.category_repository import CategoryRepository

# Importaciones de Docs (ajusta rutas si es necesario)
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
    categories = CategoryRepository.get_all_active()
    paginator = Pagination()
    paginated_categories = paginator.paginate_queryset(categories, request)
    # Pasamos el contexto para que el serializer pueda acceder al request si es necesario
    serializer = CategorySerializer(paginated_categories, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_category_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly]) # Permiso más específico que IsAuthenticated
def create_category(request):
    """
    Crea una nueva categoría.
    La lógica de asignar 'created_by' está en BaseSerializer/BaseModel.
    """
    serializer = CategorySerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        # Llamamos a serializer.save() pasando el usuario.
        # Esto ejecutará BaseSerializer.create(), que a su vez llamará
        # a Category.objects.create(..., user=request.user),
        # permitiendo a BaseModel.save() asignar created_by.
        category_instance = serializer.save(user=request.user)
        # Devolvemos la instancia creada, serializada de nuevo para obtener todos los campos
        return Response(CategorySerializer(category_instance, context={'request': request}).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_category_by_id_doc)
@extend_schema(**update_category_by_id_doc)
@extend_schema(**delete_category_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def category_detail(request, category_pk):
    """
    Obtiene, actualiza o realiza un soft delete de una categoría específica.
    """
    # Usamos el repositorio solo para obtener la instancia inicial
    category = CategoryRepository.get_by_id(category_pk)
    if not category:
        return Response({"detail": "Categoría no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    # --- GET ---
    if request.method == 'GET':
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)

    # --- PUT ---
    elif request.method == 'PUT':
        # Usamos el serializer para validar y actualizar. partial=True permite act. parciales.
        serializer = CategorySerializer(category, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            # Llamamos a serializer.save() pasando el usuario.
            # Esto ejecutará BaseSerializer.update(), que llamará a instance.save(user=...)
            # permitiendo a BaseModel.save() asignar modified_by/modified_at.
            updated_category = serializer.save(user=request.user)
            # Devolvemos la instancia actualizada y serializada
            return Response(CategorySerializer(updated_category, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- DELETE (Soft Delete usando el Serializer) ---
    elif request.method == 'DELETE':
        # Usamos el serializer para realizar el soft delete de forma consistente
        # Pasamos 'status': False y dejamos que BaseSerializer.update maneje la lógica
        serializer = CategorySerializer(category, data={'status': False}, context={'request': request}, partial=True)
        if serializer.is_valid():
             # Llamamos a save pasando el usuario. BaseSerializer.update detectará
             # status=False y llamará a instance.save(user=...) que actualizará
             # status, deleted_at y deleted_by via BaseModel.save o directamente.
             # NOTA: La implementación actual de BaseSerializer.update ya asigna
             # deleted_at/by directamente ANTES de llamar a save.
             serializer.save(user=request.user)
             return Response(status=status.HTTP_204_NO_CONTENT) # Éxito sin contenido
        else:
            return Response({"detail": "No autorizado para eliminar esta categoría."}, status=status.HTTP_403_FORBIDDEN)
