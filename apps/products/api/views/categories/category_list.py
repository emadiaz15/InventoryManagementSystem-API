# apps/products/api/views/category_list.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.products.models import Category
from ...serializers import CategorySerializer
from drf_spectacular.utils import extend_schema

@extend_schema(
    methods=['GET'],
    operation_id="list_categories",
    description="Retrieve a list of all categories",
    responses={200: CategorySerializer(many=True)},
)
@extend_schema(
    methods=['POST'],
    operation_id="create_category",
    description="Create a new category",
    request=CategorySerializer,
    responses={
        201: CategorySerializer,
        400: "Bad Request - Invalid data",
    },
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def category_list(request):
    """
    Endpoint para obtener una lista de categorías o crear una nueva categoría.
    """
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            # Asociar la categoría con el usuario autenticado, si es necesario
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
