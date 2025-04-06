from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema

# Ajusta las rutas de importación según tu estructura
from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination
from apps.products.api.serializers.product_serializer import ProductSerializer
from apps.products.api.repositories.product_repository import ProductRepository
# Quita importaciones de modelos si no se usan directamente en la vista
# from apps.products.models import Product
# from apps.products.models import Subproduct
# Quita otros serializers si no se usan directamente aquí
# from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
# from apps.stocks.api.serializers import StockProductSerializer
from apps.products.docs.product_doc import (
    list_product_doc, create_product_doc, get_product_by_id_doc,
    update_product_by_id_doc, delete_product_by_id_doc
)

@extend_schema(**list_product_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def product_list(request):
    """
    Vista para listar todos los productos activos con paginación.
    Ordenados por defecto por fecha de creación descendente (de BaseModel).
    """
    products = ProductRepository.get_all_active_products() # Obtiene queryset ordenado por Meta
    paginator = Pagination()
    paginated_products = paginator.paginate_queryset(products, request)
    # Pasa contexto al serializer
    serializer = ProductSerializer(paginated_products, many=True, context={'request': request})
    # Se elimina la lógica extra de comentarios/subproductos para claridad
    return paginator.get_paginated_response(serializer.data)

@extend_schema(**create_product_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_product(request):
    """
    Vista para crear un nuevo producto usando el serializer.
    """
    serializer = ProductSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        # Correcto: Usar serializer.save() pasando el user
        # BaseSerializer.create y BaseModel.save se encargan del resto
        product_instance = serializer.save(user=request.user)
        # Serializa la instancia creada para la respuesta
        return Response(ProductSerializer(product_instance, context={'request': request}).data, status=status.HTTP_201_CREATED)
    # Errores de validación del serializer
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(**get_product_by_id_doc)
@extend_schema(**update_product_by_id_doc)
@extend_schema(**delete_product_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def product_detail(request, prod_pk):
    """
    Vista para obtener, actualizar o realizar un soft delete de un producto específico.
    """
    product = ProductRepository.get_by_id(prod_pk) # Obtiene instancia con repositorio
    if not product:
        return Response({"detail": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Correcto: Serializa con contexto
        serializer = ProductSerializer(product, context={'request': request})
        # Se elimina la lógica extra de comentarios/subproductos para claridad
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Correcto: Usa serializer para validar y actualizar (con partial=True)
        serializer = ProductSerializer(product, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            # Correcto: Usa serializer.save() pasando el user
            updated_product = serializer.save(user=request.user)
            # Devuelve instancia actualizada serializada
            return Response(ProductSerializer(updated_product, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Correcto: Usa serializer para soft delete
        serializer = ProductSerializer(product, data={'status': False}, context={'request': request}, partial=True)
        if serializer.is_valid():
             serializer.save(user=request.user) # BaseSerializer.update maneja el soft delete
             return Response(status=status.HTTP_204_NO_CONTENT)
        else:
<<<<<<< HEAD
            return Response({"detail": "No autorizado para eliminar este producto."}, status=status.HTTP_403_FORBIDDEN)
=======
             # Error improbable si solo se envía status=False
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
>>>>>>> develop
