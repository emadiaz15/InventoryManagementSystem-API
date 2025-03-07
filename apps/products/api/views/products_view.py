from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.contenttypes.models import ContentType

from apps.core.pagination import Pagination
from apps.products.models import Product
from apps.stocks.models import Stock
from apps.comments.models import Comment
from apps.products.api.serializers.product_serializer import ProductSerializer
from apps.stocks.api.serializers import StockSerializer
from apps.comments.api.serializers import CommentSerializer
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.users.permissions import IsStaffOrReadOnly
from drf_spectacular.utils import extend_schema
from apps.products.api.repositories.product_repository import ProductRepository
from apps.products.docs.product_doc import (
    list_product_doc, create_product_doc, get_product_by_id_doc,
    update_product_by_id_doc, delete_product_by_id_doc
)

@extend_schema(**list_product_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def product_list(request):
    """
    Obtiene una lista de productos con paginación y filtros por categoría, tipo y estado.
    """
    category_id = request.query_params.get('category')
    type_id = request.query_params.get('type')
    active = request.query_params.get('status', 'true').lower() == 'true'

    products = ProductRepository.get_all_active(category_id, type_id, active)
    paginator = Pagination()
    paginated_products = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(paginated_products, many=True)
    return paginator.get_paginated_response(serializer.data)

@extend_schema(**create_product_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_product(request):
    """
    Crea un nuevo producto con un stock inicial opcional.
    """
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        # Obtener datos del request y validar el código
        code = request.data.get('code')
        stock_quantity = request.data.get('stock_quantity')

        try:
            product = ProductRepository.create(
                name=serializer.validated_data['name'],
                description=serializer.validated_data['description'],
                category=serializer.validated_data['category'],
                type=serializer.validated_data['type'],
                user=request.user,
                stock_quantity=stock_quantity,
                code=code  # Aseguramos que el `code` sea pasado al crear el producto
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_product_by_id_doc)
@extend_schema(**update_product_by_id_doc)
@extend_schema(**delete_product_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def product_detail(request, pk):
    """
    Obtiene, actualiza o realiza un soft delete de un producto específico.
    """
    product = ProductRepository.get_by_id(pk)
    if not product:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # Aseguramos la existencia de al menos un registro de stock, si no existe
    stock, created = Stock.objects.get_or_create(
        product=product,
        defaults={'quantity': 0, 'user': request.user}
    )
    stock_serializer = StockSerializer(stock)

    # Obtener comentarios del producto
    content_type = ContentType.objects.get_for_model(Product)
    comments = Comment.active_objects.filter(content_type=content_type, object_id=product.id)
    comment_serializer = CommentSerializer(comments, many=True)

    # Obtener subproductos activos
    subproducts = product.subproducts.filter(status=True)  # Solo subproductos activos
    subproduct_serializer = SubProductSerializer(subproducts, many=True)

    # Creamos la respuesta
    response_data = {
        'product': ProductSerializer(product).data,  # Incluimos los detalles del producto
        'stock': stock_serializer.data,  # Incluimos el stock del producto
    }

    # Los subproductos ya están dentro de los datos del producto, solo los agregamos correctamente
    response_data['product']['subproducts'] = subproduct_serializer.data

    # Devolvemos la respuesta
    return Response(response_data, status=status.HTTP_200_OK)
