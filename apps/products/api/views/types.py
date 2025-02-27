# Este archivo define los endpoints para listar, crear, obtener, actualizar y eliminar (de manera suave) tipos de productos.
# Ahora se aplican permisos para que todos los usuarios autenticados puedan leer (GET),
# pero solo los usuarios con is_staff=True puedan crear, actualizar y eliminar.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema

from apps.products.models import Type
from ..serializers import TypeSerializer
from apps.users.permissions import IsStaffOrReadOnly  # Importamos el permiso personalizado
from apps.core.pagination import Pagination  # Importamos la clase de paginación global


@extend_schema(
    methods=['GET'],
    operation_id="list_types",
    description="Recupera una lista de todos los tipos activos con paginación, ordenados del más nuevo al más antiguo.",
    responses={200: TypeSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])  # Permiso que da lectura a todos los autenticados y escritura solo a staff
def type_list(request):
    """
    Endpoint para listar solo los tipos activos con paginación.
    
    - Todos los usuarios autenticados pueden acceder a este endpoint.
    - Devuelve una lista de tipos con status=True, ordenados del más reciente al más antiguo.
    - Se puede modificar el número de resultados por página usando el parámetro `page_size`.
    """
    # Filtra solo los tipos que están activos en la base de datos y ordena por más reciente
    types = Type.objects.filter(status=True).order_by('-created_at')

    # Aplica la paginación usando la clase definida en core/pagination.py
    paginator = Pagination()
    paginated_types = paginator.paginate_queryset(types, request)

    # Serializa los datos de la página actual
    serializer = TypeSerializer(paginated_types, many=True)

    # Devuelve los datos serializados con la respuesta paginada
    return paginator.get_paginated_response(serializer.data)


@extend_schema(
    methods=['POST'],
    operation_id="create_type",
    description="Crea un nuevo tipo.",
    request=TypeSerializer,
    responses={
        201: TypeSerializer,
        400: "Solicitud Incorrecta - Datos inválidos",
    },
)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])  # Solo el staff puede crear
def create_type(request):
    """
    Endpoint para crear un nuevo tipo.
    
    - Requiere que el usuario sea staff para poder crear.
    - Serializa los datos recibidos, los valida y crea un tipo.
    """
    serializer = TypeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['GET'],
    operation_id="retrieve_type",
    description="Recupera detalles de un tipo específico.",
    responses={200: TypeSerializer, 404: "Tipo no encontrado"},
)
@extend_schema(
    methods=['PUT'],
    operation_id="update_type",
    description="Actualiza detalles de un tipo específico.",
    request=TypeSerializer,
    responses={
        200: TypeSerializer,
        400: "Solicitud Incorrecta - Datos inválidos",
    },
)
@extend_schema(
    methods=['DELETE'],
    operation_id="delete_type",
    description="Marca un tipo específico como inactivo en lugar de eliminarlo físicamente.",
    responses={204: "Tipo eliminado (soft) correctamente", 404: "Tipo no encontrado"},
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])  # Solo staff puede actualizar o eliminar; autenticados pueden leer
def type_detail(request, pk):
    """
    Endpoint para obtener, actualizar o marcar un tipo específico como inactivo.
    
    - GET: cualquier usuario autenticado puede obtener los detalles.
    - PUT: solo usuarios staff pueden actualizar el tipo.
    - DELETE: solo usuarios staff pueden eliminarlo (soft delete).
    """
    try:
        type_instance = Type.objects.get(pk=pk)
    except Type.DoesNotExist:
        return Response({"detail": "Tipo no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = TypeSerializer(type_instance)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = TypeSerializer(type_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        type_instance.status = False  # Soft delete (cambio de estado)
        type_instance.save()
        return Response(
            {"detail": "Tipo eliminado (soft) correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )
