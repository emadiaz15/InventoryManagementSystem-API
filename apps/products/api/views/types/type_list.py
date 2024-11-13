# apps/products/api/views/type_list.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.products.models import Type
from ...serializers import TypeSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(
    methods=['GET'],
    operation_id="list_types",
    description="Retrieve a list of all types",
    responses={200: TypeSerializer(many=True)},
)
@extend_schema(
    methods=['POST'],
    operation_id="create_type",
    description="Create a new type",
    request=TypeSerializer,
    responses={
        201: TypeSerializer,
        400: "Bad Request - Invalid data",
    },
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def type_list(request):
    """
    Endpoint para listar tipos o crear un nuevo tipo.
    """
    if request.method == 'GET':
        types = Type.objects.all()
        serializer = TypeSerializer(types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = TypeSerializer(data=request.data)
        if serializer.is_valid():
            # Asociar el usuario autenticado si el modelo lo requiere
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
