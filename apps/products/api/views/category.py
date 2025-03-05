from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.products.models import Category
from ..serializers import CategorySerializer
from apps.users.permissions import IsStaffOrReadOnly  # Importamos la clase de permisos personalizada
from apps.core.pagination import Pagination  # Importamos la clase de paginación


@extend_schema(
    methods=['GET'],
    operation_id="list_categories",
    description="Recupera una lista de todas las categorías activas con paginación, ordenadas de las más recientes a las más antiguas",
    responses={200: CategorySerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])  # Aplica permiso: lectura para todos los autenticados, cambios solo staff
def category_list(request):
    """
    Lista todas las categorías activas con paginación.
    """
    categories = Category.objects.filter(status=True).order_by('-created_at')
    paginator = Pagination()
    paginated_categories = paginator.paginate_queryset(categories, request)
    serializer = CategorySerializer(paginated_categories, many=True)
    return paginator.get_paginated_response(serializer.data)


@extend_schema(
    methods=['POST'],
    operation_id="create_category",
    description="Crea una nueva categoría",
    request=CategorySerializer,
    responses={201: CategorySerializer, 400: "Solicitud Incorrecta - Datos inválidos"},
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Asegura que solo usuarios autenticados puedan crear categorías
def create_category(request):
    """
    Crea una nueva categoría y asigna `created_by` al usuario autenticado.
    """
    serializer = CategorySerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()  # No es necesario pasar user, ya lo toma del contexto
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['GET'],
    operation_id="retrieve_category",
    description="Recupera detalles de una categoría específica",
    responses={200: CategorySerializer, 404: "Categoría no encontrada"},
)
@extend_schema(
    methods=['PUT'],
    operation_id="update_category",
    description="Actualiza detalles de una categoría específica",
    request=CategorySerializer,
    responses={200: CategorySerializer, 400: "Solicitud Incorrecta - Datos inválidos"},
)
@extend_schema(
    methods=['DELETE'],
    operation_id="delete_category",
    description="Marca una categoría específica como inactiva",
    responses={204: "Categoría eliminada (soft) correctamente", 404: "Categoría no encontrada"},
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])  # Solo staff puede actualizar o eliminar; autenticados pueden leer.
def category_detail(request, pk):
    """
    Obtiene, actualiza o realiza un soft delete de una categoría específica.
    """
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({"detail": "Categoría no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save(modified_by=request.user)  # 🔥 Asigna el usuario que realiza la modificación
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    elif request.method == 'DELETE':
        category.status = False  # Soft delete
        category.save(update_fields=['status', 'deleted_at', 'deleted_by'])
        return Response(
            {"detail": "Categoría eliminada (soft) correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )
