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
from apps.products.models.category_model import Category
from apps.products.filters.category_filter import CategoryFilter

@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def category_list(request):
    """
    Lista todas las categorías ACTIVAS con paginación y filtro por nombre.
    """
    # 1. Queryset Base: Obtener SOLO las categorías ACTIVAS.
    #    El ordenamiento por defecto (-created_at) viene de BaseModel.Meta.
    queryset = Category.objects.filter(status=True).select_related('created_by') # <-- Filtrar por status=True AQUÍ

    # 2. Aplicar Filtro de Nombre: Pasamos el request.GET y el queryset base (ya filtrado por activas).
    filterset = CategoryFilter(request.GET, queryset=queryset)
    # El filterset ahora solo aplicará el filtro 'name' si viene en request.GET

    filtered_queryset = filterset.qs # .qs contiene el queryset filtrado por nombre (y ya por status=True)

    # 3. Paginación
    paginator = Pagination()
    paginated_categories = paginator.paginate_queryset(filtered_queryset, request)

    # 4. Serialización (con contexto)
    serializer = CategorySerializer(paginated_categories, many=True, context={'request': request})

    # 5. Respuesta
    return paginator.get_paginated_response(serializer.data)

@extend_schema(**create_category_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
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
             # Esto no debería pasar si solo enviamos status=False, pero por si acaso
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
