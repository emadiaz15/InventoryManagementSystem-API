# Este archivo define los endpoints para listar, crear, obtener, actualizar y eliminar (de manera suave) categorías de productos en la API.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.products.models import Category
from ..serializers import CategorySerializer
from drf_spectacular.utils import extend_schema

# Vista para listar todas las categorías activas
@extend_schema(
    methods=['GET'],
    operation_id="list_categories",
    description="Recupera una lista de todas las categorías",
    responses={200: CategorySerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_list(request):
    """
    Endpoint para listar solo las categorías activas.
    """
    # Recupera todas las categorías activas de la base de datos
    categories = Category.objects.filter(status=True)
    # Serializa los datos para enviarlos en la respuesta
    serializer = CategorySerializer(categories, many=True)
    # Devuelve los datos serializados con un código de estado HTTP 200 OK
    return Response(serializer.data, status=status.HTTP_200_OK)

# Vista para crear una nueva categoría
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
@permission_classes([IsAuthenticated])
def create_category(request):
    """
    Endpoint para crear una nueva categoría.
    """
    # Serializa los datos recibidos en la solicitud
    serializer = CategorySerializer(data=request.data)
    # Valida los datos y, si son válidos, guarda la nueva categoría asociada al usuario autenticado
    if serializer.is_valid():
        serializer.save(user=request.user)  # Asocia la categoría con el usuario autenticado
        # Responde con los datos de la nueva categoría y un código de estado HTTP 201 CREATED
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # Si los datos no son válidos, responde con los errores de validación y un código HTTP 400 BAD REQUEST
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vista para obtener, actualizar o eliminar una categoría específica
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
@permission_classes([IsAuthenticated])
def category_detail(request, pk):
    """
    Endpoint para obtener, actualizar o eliminar una categoría específica.
    """
    # Intenta obtener la categoría por su clave primaria (pk); si no existe, responde con un error 404
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({"detail": "Categoría no encontrada."}, status=status.HTTP_404_NOT_FOUND)
    
    # Maneja la solicitud GET para obtener detalles de la categoría
    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    
    # Maneja la solicitud PUT para actualizar los detalles de la categoría
    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        # Responde con errores de validación si los datos no son válidos
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Maneja la solicitud DELETE para marcar la categoría como inactiva
    elif request.method == 'DELETE':
        category.delete()
        # Devuelve una respuesta de éxito indicando que la categoría ha sido eliminada (soft)
        return Response(
            {"detail": "Categoría eliminada (soft) correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )
