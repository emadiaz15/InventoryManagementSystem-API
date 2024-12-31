from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from django.contrib.contenttypes.models import ContentType

from apps.core.pagination import Pagination
from apps.products.models import Product
from apps.stocks.models import Stock
from apps.comments.models import Comment
from apps.stocks.api.serializers import StockSerializer
from apps.comments.api.serializers import CommentSerializer
from ..serializers import ProductSerializer
from apps.users.permissions import IsStaffOrReadOnly


@extend_schema(
    methods=['GET'],
    operation_id="list_products",
    description="Recupera una lista de todos los productos o filtra por categoría o tipo",
    parameters=[
        {
            'name': 'category',
            'in': 'query',
            'description': 'Filtra productos por ID de categoría',
            'required': False,
            'schema': {'type': 'integer'}
        },
        {
            'name': 'type',
            'in': 'query',
            'description': 'Filtra productos por ID de tipo',
            'required': False,
            'schema': {'type': 'integer'}
        },
        {
            'name': 'status',
            'in': 'query',
            'description': 'Filtra productos activos',
            'required': False,
            'schema': {'type': 'boolean'}
        },
    ],
    responses={200: ProductSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def product_list(request):
    category_id = request.query_params.get('category')
    type_id = request.query_params.get('type')
    active = request.query_params.get('status', 'true').lower() == 'true'

    products = Product.objects.filter(status=active)
    if category_id:
        products = products.filter(category_id=category_id)
    if type_id:
        products = products.filter(type_id=type_id)

    paginator = Pagination()
    paginated_products = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(paginated_products, many=True)
    return paginator.get_paginated_response(serializer.data)


@extend_schema(
    methods=['POST'],
    operation_id="create_product",
    description="Crea un nuevo producto. Si se incluye stock_quantity, se creará un registro de Stock inicial.",
    request=ProductSerializer,
    responses={
        201: ProductSerializer,
        400: "Solicitud Incorrecta - Datos inválidos"
    },
)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_product(request):
    """
    Crea un nuevo producto. Opcionalmente, puede añadir stock inicial
    si se incluye 'stock_quantity' en la petición.
    """
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save(user=request.user)

        # Si se envía un valor de stock_quantity, creamos el Stock inicial
        stock_quantity = request.data.get('stock_quantity')
        if stock_quantity is not None:
            if stock_quantity < 0:
                return Response(
                    {"detail": "Stock quantity cannot be negative."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Stock.objects.create(product=product, quantity=stock_quantity, user=request.user)

        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['GET'],
    operation_id="retrieve_product",
    description="Recupera detalles de un producto específico, incluyendo su stock y comentarios",
    responses={
        200: ProductSerializer,
        404: "Producto no encontrado"
    },
)
@extend_schema(
    methods=['PUT'],
    operation_id="update_product",
    description="Actualiza los detalles de un producto específico y opcionalmente actualiza stock.",
    request=ProductSerializer,
    responses={
        200: ProductSerializer,
        400: "Solicitud Incorrecta - Datos inválidos"
    },
)
@extend_schema(
    methods=['DELETE'],
    operation_id="delete_product",
    description="Elimina suavemente un producto específico estableciendo status en False",
    responses={
        204: "Producto marcado como inactivo",
        404: "Producto no encontrado"
    },
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def product_detail(request, pk):
    """
    Obtiene, actualiza o realiza soft-delete de un producto específico.
    También retorna/actualiza la cantidad de Stock si se envía 'stock_quantity'.
    """
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    # Aseguramos la existencia de al menos un registro de stock, si no existe
    stock, created = Stock.objects.get_or_create(
        product=product,
        defaults={'quantity': 0, 'user': request.user}
    )
    stock_serializer = StockSerializer(stock)

    # Obtener comentarios
    content_type = ContentType.objects.get_for_model(Product)
    comments = Comment.active_objects.filter(content_type=content_type, object_id=product.id)
    comment_serializer = CommentSerializer(comments, many=True)

    if request.method == 'GET':
        product_serializer = ProductSerializer(product)
        return Response({
            'product': product_serializer.data,
            'stock': stock_serializer.data,
            'comments': comment_serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Actualizamos el producto (parcialmente si es necesario)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            product = serializer.save()

            # Si se envía stock_quantity, actualizamos la cantidad de stock
            stock_quantity = request.data.get('stock_quantity')
            if stock_quantity is not None:
                if stock_quantity < 0:
                    return Response(
                        {"detail": "Stock quantity cannot be negative."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                stock.quantity = stock_quantity
                stock.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        product.status = False
        product.save()
        return Response({"detail": "Product set to inactive successfully."}, status=status.HTTP_204_NO_CONTENT)
