# Este archivo define los endpoints para listar, crear, obtener, actualizar y eliminar (de manera suave) productos en la API.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from ...pagination import ProductPagination
from ...models import Product
from apps.stocks.models import Stock
from ..serializers import ProductSerializer
from drf_spectacular.utils import extend_schema
import base64
from django.core.files.base import ContentFile

# Vista para listar productos activos con filtros opcionales de categoría y tipo
@extend_schema(
    methods=['GET'],
    operation_id="list_products",
    description="Recupera una lista de todos los productos o filtra por categoría o tipo",
    parameters=[
        {'name': 'category', 'in': 'query', 'description': 'Filtra productos por ID de categoría', 'required': False, 'schema': {'type': 'integer'}},
        {'name': 'type', 'in': 'query', 'description': 'Filtra productos por ID de tipo', 'required': False, 'schema': {'type': 'integer'}},
        {'name': 'is_active', 'in': 'query', 'description': 'Filtra productos activos', 'required': False, 'schema': {'type': 'boolean'}},
    ],
    responses={200: ProductSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_list(request):
    """
    Endpoint para listar productos con opción de filtrar por categoría, tipo y estado.
    """
    category_id = request.query_params.get('category')
    type_id = request.query_params.get('type')
    is_active = request.query_params.get('is_active', 'true').lower() == 'true'

    # Filtra los productos según el estado activo, categoría y tipo
    products = Product.objects.filter(is_active=is_active)
    if category_id:
        products = products.filter(category_id=category_id)
    if type_id:
        products = products.filter(type_id=type_id)

    # Aplica paginación a los productos filtrados
    paginator = ProductPagination()
    paginated_products = paginator.paginate_queryset(products, request)
    
    # Serializa y retorna los productos paginados
    serializer = ProductSerializer(paginated_products, many=True)
    return paginator.get_paginated_response(serializer.data)


# Vista para crear un nuevo producto
@extend_schema(
    methods=['POST'],
    operation_id="create_product",
    description="Crea un nuevo producto",
    request=ProductSerializer,
    responses={
        201: ProductSerializer,
        400: "Solicitud Incorrecta - Datos inválidos",
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    """
    Endpoint para crear un nuevo producto.
    """
    # Serializa los datos recibidos en la solicitud
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        # Guarda el producto con el usuario autenticado como creador
        product = serializer.save(user=request.user)

        # Procesa la imagen de ficha técnica si está en `metadata` y en formato Base64
        metadata = request.data.get('metadata', {})
        if 'technical_sheet_photo' in metadata:
            try:
                format, imgstr = metadata['technical_sheet_photo'].split(';base64,')
                ext = format.split('/')[-1]
                product.image = ContentFile(base64.b64decode(imgstr), name=f"{product.name}_tech_sheet.{ext}")
            except Exception as e:
                return Response({"detail": f"Error al decodificar la foto de la ficha técnica: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        product.save()

        # Crea un stock inicial si se proporciona la cantidad
        if 'stock_quantity' in request.data:
            Stock.objects.create(product=product, quantity=request.data['stock_quantity'], user=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Responde con errores de validación
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Vista para obtener, actualizar o eliminar un producto específico
@extend_schema(
    methods=['GET'],
    operation_id="retrieve_product",
    description="Recupera detalles de un producto específico, incluyendo su stock",
    responses={200: ProductSerializer, 404: "Producto no encontrado"},
)
@extend_schema(
    methods=['PUT'],
    operation_id="update_product",
    description="Actualiza los detalles de un producto específico y opcionalmente actualiza stock o metadata",
    request=ProductSerializer,
    responses={200: ProductSerializer, 400: "Solicitud Incorrecta - Datos inválidos"},
)
@extend_schema(
    methods=['DELETE'],
    operation_id="delete_product",
    description="Elimina suavemente un producto específico estableciendo is_active en False",
    responses={204: "Producto marcado como inactivo", 404: "Producto no encontrado"},
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, pk):
    """
    Endpoint para obtener, actualizar o eliminar (suavemente) un producto específico.
    """
    # Intenta obtener el producto por su clave primaria (pk); si no existe, responde con un error 404
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    # Maneja la solicitud GET para obtener detalles del producto
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Maneja la solicitud PUT para actualizar los detalles del producto
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            product = serializer.save()

            # Procesa la imagen de ficha técnica si está en `metadata` y en formato Base64
            metadata = request.data.get('metadata', {})
            if 'technical_sheet_photo' in metadata:
                try:
                    format, imgstr = metadata['technical_sheet_photo'].split(';base64,')
                    ext = format.split('/')[-1]
                    product.image = ContentFile(base64.b64decode(imgstr), name=f"{product.name}_tech_sheet.{ext}")
                except Exception as e:
                    return Response({"detail": f"Error al decodificar la foto de la ficha técnica: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualiza valores en `metadata` si se proporcionan
            for key, value in metadata.items():
                product.metadata[key] = value
            product.save()

            # Actualiza el stock si se proporciona una nueva cantidad
            stock_quantity = request.data.get('stock_quantity')
            if stock_quantity is not None:
                stock, _ = Stock.objects.get_or_create(product=product, defaults={'user': request.user, 'quantity': stock_quantity})
                stock.quantity = stock_quantity
                stock.save()
                
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Maneja la solicitud DELETE para marcar el producto como inactivo
    elif request.method == 'DELETE':
        product.is_active = False
        product.save()
        return Response({"detail": "Producto marcado como inactivo correctamente."}, status=status.HTTP_204_NO_CONTENT)
