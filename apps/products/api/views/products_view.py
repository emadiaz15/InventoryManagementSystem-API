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

    if request.method == 'GET':
        # Obtener stock y comentarios
        stock, created = Stock.objects.get_or_create(
            product=product,
            defaults={'quantity': 0, 'user': request.user}
        )
        stock_serializer = StockSerializer(stock)

        content_type = ContentType.objects.get_for_model(Product)
        comments = Comment.active_objects.filter(content_type=content_type, object_id=product.id)
        comment_serializer = CommentSerializer(comments, many=True)

        product_serializer = ProductSerializer(product)
        return Response({
            'product': product_serializer.data,
            'stock': stock_serializer.data,
            'comments': comment_serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Actualizar producto
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            code = request.data.get('code')
            if code is not None:
                try:
                    # Verificar que el código sea válido
                    product = ProductRepository.update(
                        product,
                        name=serializer.validated_data.get('name'),
                        description=serializer.validated_data.get('description'),
                        category=serializer.validated_data.get('category'),
                        type=serializer.validated_data.get('type'),
                        status=serializer.validated_data.get('status'),
                        code=code,  # Validamos el código también en la actualización
                        user=request.user
                    )
                except ValueError as e:
                    return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Solo actualizamos sin cambiar el código
                product = ProductRepository.update(
                    product,
                    name=serializer.validated_data.get('name'),
                    description=serializer.validated_data.get('description'),
                    category_id=serializer.validated_data.get('category'),
                    type_id=serializer.validated_data.get('type'),
                    status=serializer.validated_data.get('status'),
                    user=request.user
                )

            # Validar y actualizar stock_quantity
            stock_quantity = request.data.get('stock_quantity')
            if stock_quantity is not None:
                try:
                    # Verificamos que 'stock_quantity' sea un número entero
                    stock_quantity = int(stock_quantity)
                    if stock_quantity < 0:
                        return Response({"detail": "La cantidad de stock no puede ser negativa."}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({"detail": "La cantidad de stock debe ser un número entero."}, status=status.HTTP_400_BAD_REQUEST)

                # Actualizar stock
                stock = Stock.objects.get(product=product)
                stock.quantity = stock_quantity
                stock.save()

            return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Soft delete del producto
        ProductRepository.soft_delete(product, request.user)
        return Response({"detail": "Producto marcado como inactivo correctamente."}, status=status.HTTP_204_NO_CONTENT)
