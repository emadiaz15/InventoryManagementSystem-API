from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.core.pagination import Pagination
from apps.products.models.category_model import Category
from apps.products.api.serializers.category_serializer import CategorySerializer
from apps.products.api.repositories.category_repository import CategoryRepository
from apps.products.filters.category_filter import CategoryFilter

from apps.products.docs.category_doc import (
    category_list_doc,
    create_category_doc,
    get_category_by_id_doc,
    update_category_by_id_doc,
    delete_category_by_id_doc
)


@extend_schema(**category_list_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_list(request):
    """
    Lista todas las categorías ACTIVAS con paginación y filtro por nombre.
    """
    queryset = Category.objects.filter(status=True).select_related('created_by')
    filterset = CategoryFilter(request.GET, queryset=queryset)
    qs = filterset.qs

    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = CategorySerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_category_doc)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_category(request):
    """
    Crea una nueva categoría.
    Solo administradores.
    """
    serializer = CategorySerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        category = serializer.save(user=request.user)
        return Response(
            CategorySerializer(category, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_category_by_id_doc)
@extend_schema(**update_category_by_id_doc)
@extend_schema(**delete_category_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def category_detail(request, category_pk):
    """
    GET:  consulta (autenticados).  
    PUT:  actualización (solo administradores).  
    DELETE: baja suave (solo administradores).
    """
    category = CategoryRepository.get_by_id(category_pk)
    if not category:
        return Response({"detail": "Categoría no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    # GET
    if request.method == 'GET':
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)

    # PUT
    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para actualizar esta categoría."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CategorySerializer(category, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            updated = serializer.save(user=request.user)
            return Response(CategorySerializer(updated, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE (soft delete)
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para eliminar esta categoría."},
                status=status.HTTP_403_FORBIDDEN
            )
        # Le pasamos status=False para soft delete
        serializer = CategorySerializer(category, data={'status': False}, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
