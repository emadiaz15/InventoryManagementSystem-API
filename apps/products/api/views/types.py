# Este archivo define los endpoints para listar, crear, obtener, actualizar y eliminar (de manera suave) tipos de productos en la API.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.products.models import Type
from ..serializers import TypeSerializer
from drf_spectacular.utils import extend_schema

# Vista para listar todos los tipos activos
@extend_schema(
    methods=['GET'],
    operation_id="list_types",
    description="Recupera una lista de todos los tipos activos",
    responses={200: TypeSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def type_list(request):
    """
    Endpoint para listar solo los tipos activos.
    """
    # Filtra solo los tipos que están activos en la base de datos
    types = Type.objects.filter(status=True)
    # Serializa los datos para enviarlos en la respuesta
    serializer = TypeSerializer(types, many=True)
    # Devuelve los datos serializados con un código de estado HTTP 200 OK
    return Response(serializer.data, status=status.HTTP_200_OK)

# Vista para crear un nuevo tipo
@extend_schema(
    methods=['POST'],
    operation_id="create_type",
    description="Crea un nuevo tipo",
    request=TypeSerializer,
    responses={
        201: TypeSerializer,
        400: "Solicitud Incorrecta - Datos inválidos",
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_type(request):
    """
    Endpoint para crear un nuevo tipo.
    """
    # Serializa los datos recibidos en la solicitud
    serializer = TypeSerializer(data=request.data)
    # Valida los datos y, si son válidos, guarda el nuevo tipo asociado al usuario autenticado
    if serializer.is_valid():
        serializer.save(user=request.user)
        # Responde con los datos del nuevo tipo y un código de estado HTTP 201 CREATED
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # Si los datos no son válidos, responde con los errores de validación y un código HTTP 400 BAD REQUEST
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vista para obtener, actualizar o eliminar un tipo específico
@extend_schema(
    methods=['GET'],
    operation_id="retrieve_type",
    description="Recupera detalles de un tipo específico",
    responses={200: TypeSerializer, 404: "Tipo no encontrado"},
)
@extend_schema(
    methods=['PUT'],
    operation_id="update_type",
    description="Actualiza detalles de un tipo específico",
    request=TypeSerializer,
    responses={
        200: TypeSerializer,
        400: "Solicitud Incorrecta - Datos inválidos",
    },
)
@extend_schema(
    methods=['DELETE'],
    operation_id="delete_type",
    description="Marca un tipo específico como inactivo",
    responses={204: "Tipo eliminado (soft)correctamente", 404: "Tipo no encontrado"},
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def type_detail(request, pk):
    """
    Endpoint para obtener, actualizar o marcar un tipo específico como inactivo.
    """
    # Intenta obtener el tipo por su clave primaria (pk); si no existe, responde con un error 404
    try:
        type_instance = Type.objects.get(pk=pk)
    except Type.DoesNotExist:
        return Response({"detail": "Tipo no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    # Maneja la solicitud GET para obtener detalles del tipo
    if request.method == 'GET':
        serializer = TypeSerializer(type_instance)
        return Response(serializer.data)
    
    # Maneja la solicitud PUT para actualizar los detalles del tipo
    elif request.method == 'PUT':
        serializer = TypeSerializer(type_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        # Responde con errores de validación si los datos no son válidos
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Maneja la solicitud DELETE para marcar el tipo como inactivo
    elif request.method == 'DELETE':
        type_instance.delete()
        # Devuelve una respuesta de éxito indicando que el tipo ha sido marcado como inactivo
        return Response(
            {"detail": "Tipo eliminado (soft) correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )
