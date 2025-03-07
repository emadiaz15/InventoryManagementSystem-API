from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination

from apps.products.models.product_model import Product
from apps.stocks.models import Stock
from apps.comments.models import Comment
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type

from apps.products.api.serializers.product_serializer import ProductSerializer
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.stocks.api.serializers import StockSerializer
from apps.comments.api.serializers import CommentSerializer

from apps.products.api.repositories.product_repository import ProductRepository
from apps.products.docs.product_doc import (
    list_product_doc, create_product_doc, get_product_by_id_doc,
    update_product_by_id_doc, delete_product_by_id_doc
)

# Vista para listar productos @extend_schema(**list_product_doc)
@extend_schema(**list_product_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def product_list(request):
    products = ProductRepository.get_all_active_products()
    paginator = Pagination()
    paginated_products = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(paginated_products, many=True)
    return paginator.get_paginated_response(serializer.data)


# Vista para crear un nuevo producto
@extend_schema(**create_product_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_product(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        code = request.data.get('code')
        try:
            # Crear el producto principal
            product = ProductRepository.create(
                name=serializer.validated_data['name'],
                description=serializer.validated_data['description'],
                category=serializer.validated_data['category'],
                type=serializer.validated_data['type'],
                user=request.user,
                code=code  # Aseguramos que el `code` se pase al crear el producto
            )

            # Si es necesario, también podrías manejar otras relaciones del producto aquí (p. ej., imágenes, etiquetas, etc.)
            # Pero el stock y los subproductos se gestionarán en otro método, como mencionaste.

        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Documentación de los endpoints
@extend_schema(**get_product_by_id_doc)
@extend_schema(**update_product_by_id_doc)
@extend_schema(**delete_product_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def product_detail(request, pk):
    """
    Obtiene, actualiza o realiza un soft delete de un producto específico.
    """
    # Intentar obtener el producto
    product = ProductRepository.get_by_id(pk)
    
    if not product:
        # Si no se encuentra, devolvemos un mensaje de error personalizado
        return Response({"detail": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        # Obtener o crear el stock para este producto
        stock, created = Stock.objects.get_or_create(product=product, defaults={'quantity': 0, 'user': request.user})
        stock_serializer = StockSerializer(stock)
        
        # Obtener los comentarios activos del producto
        content_type = ContentType.objects.get_for_model(Product)
        comments = Comment.active_objects.filter(content_type=content_type, object_id=product.id)
        comment_serializer = CommentSerializer(comments, many=True)
        
        # Obtener subproductos activos
        subproducts = product.subproducts.filter(status=True)  # Asegúrate de que `status` sea un campo booleano
        subproduct_serializer = SubProductSerializer(subproducts, many=True)
        
        # Crear la respuesta con todos los detalles
        response_data = {
            'product': ProductSerializer(product).data,  # Detalles del producto
            'stock': stock_serializer.data,  # Detalles del stock
            'comments': comment_serializer.data,  # Comentarios del producto
            'subproducts': subproduct_serializer.data  # Subproductos activos
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Aquí manejaríamos la lógica de actualización del producto
        serializer = ProductSerializer(product, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Guardamos el producto, pasando el usuario y la fecha de modificación
            updated_product = serializer.save(modified_by=request.user, modified_at=timezone.now())
            
            # Si también se recibe stock_quantity, actualizamos el stock
            stock_quantity = request.data.get('stock_quantity')
            if stock_quantity is not None:
                stock = Stock.objects.filter(product=updated_product).first()
                if stock:
                    stock.quantity = stock_quantity
                    stock.save(user=request.user)
                else:
                    Stock.objects.create(product=updated_product, quantity=stock_quantity, user=request.user)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        user = request.user if request.user.is_authenticated else None
        if user:
            # Realizamos un soft delete usando el repositorio
            updated_product =ProductRepository.soft_delete(product, user)
            return Response(
                {"detail": "Producto eliminada (soft) correctamente."},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response({"detail": "No autorizado para eliminar esta categoría."}, status=status.HTTP_403_FORBIDDEN)
