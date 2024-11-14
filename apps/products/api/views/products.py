from rest_framework.pagination import PageNumberPagination
from ...pagination import ProductPagination
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from ...models import Product
from apps.stocks.models import Stock
from ..serializers import ProductSerializer
from drf_spectacular.utils import extend_schema
import base64
from django.core.files.base import ContentFile

@extend_schema(
    methods=['GET'],
    operation_id="list_products",
    description="Retrieve a list of all products or filter by category or type",
    parameters=[
        {'name': 'category', 'in': 'query', 'description': 'Filter products by category ID', 'required': False, 'schema': {'type': 'integer'}},
        {'name': 'type', 'in': 'query', 'description': 'Filter products by type ID', 'required': False, 'schema': {'type': 'integer'}},
        {'name': 'is_active', 'in': 'query', 'description': 'Filter active products', 'required': False, 'schema': {'type': 'boolean'}},
    ],
    responses={200: ProductSerializer(many=True)},
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_list(request):
    if request.method == 'GET':
        category_id = request.query_params.get('category')
        type_id = request.query_params.get('type')
        is_active = request.query_params.get('is_active', 'true').lower() == 'true'

        # Filtrar productos según la categoría, el tipo y el estado
        products = Product.objects.filter(is_active=is_active)
        if category_id:
            products = products.filter(category_id=category_id)
        if type_id:
            products = products.filter(type_id=type_id)

        # Paginación
        paginator = ProductPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        
        # Serialización de productos
        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save(user=request.user)

            # Manejo de imagen en metadata si está en formato Base64
            metadata = request.data.get('metadata', {})
            if 'technical_sheet_photo' in metadata:
                try:
                    format, imgstr = metadata['technical_sheet_photo'].split(';base64,')
                    ext = format.split('/')[-1]
                    product.image = ContentFile(base64.b64decode(imgstr), name=f"{product.name}_tech_sheet.{ext}")
                except Exception as e:
                    return Response({"detail": f"Error decoding technical sheet photo: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            product.save()

            # Crear stock inicial si se proporciona
            if 'stock_quantity' in request.data:
                Stock.objects.create(product=product, quantity=request.data['stock_quantity'], user=request.user)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Responder con errores de validación
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['GET'],
    operation_id="retrieve_product",
    description="Retrieve details of a specific product, including its stock",
    responses={200: ProductSerializer, 404: "Product not found"},
)
@extend_schema(
    methods=['PUT'],
    operation_id="update_product",
    description="Update details of a specific product and optionally update stock or metadata",
    request=ProductSerializer,
    responses={200: ProductSerializer, 400: "Bad Request - Invalid data"},
)
@extend_schema(
    methods=['DELETE'],
    operation_id="delete_product",
    description="Soft delete a specific product by setting its is_active flag to False",
    responses={204: "Product marked as inactive", 404: "Product not found"},
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            product = serializer.save()

            # Procesar la imagen de ficha técnica si está en `metadata` y en formato Base64
            metadata = request.data.get('metadata', {})
            if 'technical_sheet_photo' in metadata:
                try:
                    format, imgstr = metadata['technical_sheet_photo'].split(';base64,')
                    ext = format.split('/')[-1]
                    product.image = ContentFile(base64.b64decode(imgstr), name=f"{product.name}_tech_sheet.{ext}")
                except Exception as e:
                    return Response({"detail": f"Error decoding technical sheet photo: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualización de valores en `metadata` si se proporcionan
            for key, value in metadata.items():
                product.metadata[key] = value
            product.save()

            # Actualización de stock si se proporciona
            stock_quantity = request.data.get('stock_quantity')
            if stock_quantity is not None:
                stock, _ = Stock.objects.get_or_create(product=product, defaults={'user': request.user, 'quantity': stock_quantity})
                stock.quantity = stock_quantity
                stock.save()
                
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Cambio del estado de `is_active` a False en lugar de eliminar el producto
        product.is_active = False
        product.save()
        return Response({"detail": "Producto marcado como inactivo correctamente."}, status=status.HTTP_204_NO_CONTENT)
