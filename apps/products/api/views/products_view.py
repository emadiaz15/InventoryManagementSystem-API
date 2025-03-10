from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError

from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination
from apps.products.api.repositories.product_repository import ProductRepository
from apps.stocks.models import ProductStock
from apps.comments.models import ProductComment

from apps.products.api.serializers.product_serializer import ProductSerializer
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.stocks.api.serializers import StockProductSerializer
from apps.comments.api.serializers import ProductCommentSerializer
from apps.products.docs.product_doc import (
    list_product_doc, create_product_doc, get_product_by_id_doc,
    update_product_by_id_doc, delete_product_by_id_doc
)

# ✅ Vista para listar productos
@extend_schema(**list_product_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def product_list(request):
    products = ProductRepository.get_all_active_products()
    paginator = Pagination()
    paginated_products = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(paginated_products, many=True)
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_product_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_product(request):
    serializer = ProductSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            # Crear el producto usando la función de repositorio, pasando solo los IDs
            product = ProductRepository.create(
                name=serializer.validated_data['name'],
                description=serializer.validated_data['description'],
                category=serializer.validated_data['category'],  # Pasar solo el ID de la categoría
                type=serializer.validated_data['type'],  # Pasar solo el ID del tipo
                user=request.user,
                code=serializer.validated_data['code']
            )
            
            # Devolver la respuesta con el producto creado
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Vista para obtener, actualizar y eliminar un producto
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
        return Response({"detail": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        stock, _ = ProductStock.objects.get_or_create(product=product, defaults={'quantity': 0, 'created_by': request.user})
        stock_serializer = StockProductSerializer(stock)

        comments = ProductComment.objects.filter(product=product, status=True)
        comment_serializer = ProductCommentSerializer(comments, many=True)

        subproducts = product.subproducts.filter(status=True)
        subproduct_serializer = SubProductSerializer(subproducts, many=True)

        return Response({
            'product': ProductSerializer(product).data,
            'stock': stock_serializer.data,
            'comments': comment_serializer.data,
            'subproducts': subproduct_serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            updated_product = serializer.save(modified_by=request.user, modified_at=timezone.now())
            
            # Actualizar stock solo si se pasa el valor en el request
            stock_quantity = request.data.get('stock_quantity')
            if stock_quantity is not None:
                ProductRepository.update_or_create_stock(updated_product, stock_quantity, request.user)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if request.user.is_authenticated:
            ProductRepository.soft_delete(product, request.user)
            return Response({"detail": "Producto eliminado correctamente (soft delete)."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "No autorizado para eliminar este producto."}, status=status.HTTP_403_FORBIDDEN)
