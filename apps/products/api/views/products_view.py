from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError

from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination
from apps.products.api.repositories.product_repository import ProductRepository
from apps.products.models import Product
from apps.products.models import Subproduct
from apps.comments.models import SubproductComment
from apps.comments.api.serializers import SubproductCommentSerializer


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
    """
    Vista para listar todos los productos activos con paginación, incluyendo comentarios.
    """
    # Obtener los productos activos, ordenados por ID
    products = ProductRepository.get_all_active_products().order_by('id')
    
    # Inicializar el paginador
    paginator = Pagination()
    paginated_products = paginator.paginate_queryset(products, request)  # Paginación de los productos
    
    # Serializar los productos
    serializer = ProductSerializer(paginated_products, many=True)
    
    # Agregar los comentarios de productos y subproductos
    for product_data in serializer.data:
        product = Product.objects.get(id=product_data['id'])  # Obtener el producto
        product_comments = ProductComment.objects.filter(product=product, status=True)  # Obtener comentarios activos
        product_data['comments'] = ProductCommentSerializer(product_comments, many=True).data  # Asignar comentarios

        # Agregar comentarios de subproductos
        for subproduct_data in product_data['subproducts']:
            subproduct = Subproduct.objects.get(id=subproduct_data['id'])  # Obtener el subproducto
            subproduct_comments = SubproductComment.objects.filter(subproduct=subproduct, status=True)  # Obtener comentarios activos de subproducto
            subproduct_data['comments'] = SubproductCommentSerializer(subproduct_comments, many=True).data  # Asignar comentarios a subproducto

    # Devolver la respuesta con los productos paginados, incluyendo comentarios
    return paginator.get_paginated_response(serializer.data)



@extend_schema(**create_product_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])  # Define tu clase de permisos según tu necesidad
def create_product(request):
    """
    Vista para crear un nuevo producto.
    """
    serializer = ProductSerializer(data=request.data, context={'request': request})  # Serializar los datos de entrada

    if serializer.is_valid():
        try:
            # Extraer los datos validados del serializador
            category_id = serializer.validated_data['category'].id  # Usar solo el ID de la categoría
            type_id = serializer.validated_data['type'].id  # Usar solo el ID del tipo
            
            # Crear el producto utilizando el repositorio
            product = ProductRepository.create(
                name=serializer.validated_data['name'],
                description=serializer.validated_data['description'],
                category_id=category_id,  # Pasar solo el ID de la categoría
                type_id=type_id,  # Pasar solo el ID del tipo
                user=request.user,
                code=serializer.validated_data['code'],
                quantity=serializer.validated_data['quantity']  # Pasar la cantidad del producto
            )
            
            # Responder con el producto creado
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            # Manejo de excepciones
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # Responder con errores si el serializador no es válido
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_product_by_id_doc)
@extend_schema(**update_product_by_id_doc)
@extend_schema(**delete_product_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def product_detail(request, prod_pk):
    """
    Vista para obtener, actualizar o realizar un soft delete de un producto específico, con sus comentarios.
    """

    product = ProductRepository.get_by_id(prod_pk)  # Obtener el producto por ID

    if not product:
        # Si no existe el producto, devolver 404
        return Response({"detail": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Serializar el producto
        product_data = ProductSerializer(product).data
        
        # Obtener los comentarios del producto
        product_comments = ProductComment.objects.filter(product=product, status=True)
        product_data['comments'] = ProductCommentSerializer(product_comments, many=True).data  # Asignar comentarios

        # Obtener los subproductos asociados al producto
        subproducts = Subproduct.objects.filter(parent=product, status=True)  # Obtener subproductos activos
        subproduct_data = SubProductSerializer(subproducts, many=True).data  # Serializar subproductos

        # Agregar comentarios de subproductos dentro de cada subproducto
        for subproduct in subproduct_data:
            subproduct_obj = Subproduct.objects.get(id=subproduct['id'])  # Obtener el subproducto por ID
            subproduct_comments = SubproductComment.objects.filter(subproduct=subproduct_obj, status=True)  # Obtener comentarios del subproducto
            subproduct['comments'] = SubproductCommentSerializer(subproduct_comments, many=True).data  # Asignar comentarios al subproducto

        # Asignar los subproductos con sus comentarios al producto
        product_data['subproducts'] = subproduct_data

        # Devolver los detalles del producto con los comentarios de producto y subproductos
        return Response(product_data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Actualizar el producto utilizando el repositorio
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            # Aquí utilizamos el repositorio para actualizar el producto
            updated_product = ProductRepository.update(

                product_id=prod_pk,
                name=serializer.validated_data['name'],
                description=serializer.validated_data['description'],
                category_id=serializer.validated_data['category'].id,
                type_id=serializer.validated_data['type'].id,
                code=serializer.validated_data['code'],
                quantity=serializer.validated_data['quantity'],
                status=serializer.validated_data['status'],
                user=request.user
            )
            if updated_product:
                return Response(ProductSerializer(updated_product).data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Error al actualizar el producto."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Eliminar el producto con soft delete
        if request.user.is_authenticated:
            ProductRepository.soft_delete(product, request.user)
            return Response({"detail": "Producto eliminado correctamente (soft delete)."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "No autorizado para eliminar este producto."}, status=status.HTTP_403_FORBIDDEN)
