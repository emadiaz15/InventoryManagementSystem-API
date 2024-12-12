# Este archivo define los endpoints para listar, crear, obtener, actualizar y eliminar (de manera suave) categorías de productos.
# Ahora se aplican permisos para que todos los usuarios autenticados puedan leer (GET),
# pero solo los usuarios con is_staff=True puedan crear, actualizar y eliminar.
# Los comentarios están en español y los mensajes se mantienen en el idioma correspondiente.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema

from apps.products.models import Category
from ..serializers import CategorySerializer
from apps.users.permissions import IsStaffOrReadOnly  # Importamos la clase de permisos personalizada
from apps.core.pagination import Pagination  # Importamos la clase de paginación

@extend_schema(
    methods=['GET'],
    operation_id="list_categories",
    description="Recupera una lista de todas las categorías activas con paginación",
    responses={200: CategorySerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])  # Aplica permiso: lectura para todos los autenticados, cambios solo staff
def category_list(request):
    """
    Endpoint para listar solo las categorías activas con paginación.
    
    - Todos los usuarios autenticados pueden acceder a este endpoint.
    - Devuelve una lista de categorías con status=True, paginada.
    - Se puede modificar el número de resultados por página usando el parámetro `page_size`.
    """
    # Recupera todas las categorías activas de la base de datos
    categories = Category.objects.filter(status=True)

    # Aplica la paginación usando la clase definida en core/pagination.py
    paginator = Pagination()
    paginated_categories = paginator.paginate_queryset(categories, request)

    # Serializa los datos de la página actual
    serializer = CategorySerializer(paginated_categories, many=True)

    # Devuelve los datos serializados con la respuesta paginada
    return paginator.get_paginated_response(serializer.data)


@extend_schema(
    methods=['POST'],
    operation_id="create_category",
    description="Crea una nueva categoría",
    request=CategorySerializer,
    responses={
        201: CategorySerializer,
        400: "Solicitud Incorrecta - Datos inválidos",
    },
)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])  # Solo el staff puede crear
def create_category(request):
    """
    Endpoint para crear una nueva categoría.
    
    - Requiere que el usuario sea staff para poder crear.
    - Serializa los datos recibidos, los valida y crea una categoría.
    """
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)  # Asocia la categoría con el usuario autenticado
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
    responses={
        200: CategorySerializer,
        400: "Solicitud Incorrecta - Datos inválidos",
    },
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
    Endpoint para obtener, actualizar o eliminar (soft) una categoría específica.
    
    - GET: cualquier usuario autenticado puede obtener los detalles.
    - PUT: solo usuarios staff pueden actualizar la categoría.
    - DELETE: solo usuarios staff pueden eliminarla (soft delete).
    """
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({"detail": "Categoría no encontrada."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        category.delete()
        return Response(
            {"detail": "Categoría eliminada (soft) correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )
