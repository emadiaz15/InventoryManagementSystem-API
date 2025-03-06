from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from django.core.files.base import ContentFile
import base64

from apps.core.pagination import Pagination
from apps.products.models import Product, CableAttributes
from apps.products.api.serializers.product_serializer import ProductSerializer
from apps.users.permissions import IsStaffOrReadOnly


def decode_image_base64(image_data, name_prefix):
    """
    Decodifica una imagen en formato Base64 y la convierte en un archivo ContentFile.
    Lanza ValueError si ocurre algún error.
    """
    try:
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        return ContentFile(base64.b64decode(imgstr), name=f"{name_prefix}_tech_sheet.{ext}")
    except Exception as e:
        raise ValueError(f"Error decoding technical sheet image: {str(e)}")


@extend_schema(
    methods=['GET'],
    operation_id="list_subproducts",
    description="Recupera una lista de subproductos (productos hijo) para un producto padre específico con paginación",
    parameters=[
        {
            'name': 'product_pk',
            'in': 'path',
            'description': 'ID del producto padre',
            'required': True,
            'schema': {'type': 'integer'}
        },
    ],
    responses={200: ProductSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])  # Usuarios autenticados leen, solo staff modifica
def subproduct_list(request, product_pk):
    """
    Endpoint para listar subproductos de un producto padre con paginación.
    
    - Un subproducto es un producto con `parent=product_padre` y status=True.
    - Todos los usuarios autenticados pueden leer (GET).
    - Se puede modificar el número de resultados por página usando el parámetro `page_size`.
    """
    try:
        parent_product = Product.objects.get(pk=product_pk, status=True)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found or inactive."}, status=status.HTTP_404_NOT_FOUND)
    
    subproducts = parent_product.subproducts.filter(status=True)

    # Aplica la paginación
    paginator = Pagination()
    paginated_subproducts = paginator.paginate_queryset(subproducts, request)
    
    # Serializa los datos de la página actual
    serializer = ProductSerializer(paginated_subproducts, many=True)

    # Devuelve la respuesta paginada
    return paginator.get_paginated_response(serializer.data)


@extend_schema(
    methods=['POST'],
    operation_id="create_subproduct",
    description="Crea un nuevo subproducto (producto hijo) asociado a un producto padre",
    request=ProductSerializer,
    responses={201: ProductSerializer, 400: "Solicitud Incorrecta - Datos inválidos"},
)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])  # Solo staff puede crear
def create_subproduct(request, product_pk):
    """
    Crea un nuevo subproducto asignando `parent = product_padre`.
    Si la categoría del producto padre o subproducto es 'Cables',
    se pueden crear o actualizar atributos en CableAttributes (campo brand, etc.).
    """
    try:
        parent_product = Product.objects.get(pk=product_pk, status=True)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found or inactive."}, status=status.HTTP_404_NOT_FOUND)

    # Forzamos el 'parent' en los datos
    data = request.data.copy()
    data['parent'] = parent_product.pk

    # Creamos el subproducto
    serializer = ProductSerializer(data=data)
    if serializer.is_valid():
        new_subproduct = serializer.save(user=request.user)

        # Si la categoría es "Cables", manejamos CableAttributes
        if new_subproduct.category and new_subproduct.category.name == "Cables":
            # Obtener (o crear) registro de CableAttributes asociado
            cable_attrs, created = CableAttributes.objects.get_or_create(parent=new_subproduct)
            
            # Leemos los campos desde el mismo nivel que el resto del producto
            cable_attrs.brand = request.data.get('brand', cable_attrs.brand)
            cable_attrs.number_coil = request.data.get('number_coil', cable_attrs.number_coil)
            cable_attrs.initial_length = request.data.get('initial_length', cable_attrs.initial_length)
            cable_attrs.total_weight = request.data.get('total_weight', cable_attrs.total_weight)
            cable_attrs.coil_weight = request.data.get('coil_weight', cable_attrs.coil_weight)
            
            # Procesar technical_sheet_photo en base64, si viene
            technical_sheet_photo_b64 = request.data.get('technical_sheet_photo')
            if technical_sheet_photo_b64:
                try:
                    cable_attrs.technical_sheet_photo = decode_image_base64(
                        technical_sheet_photo_b64,
                        new_subproduct.name
                    )
                except ValueError as e:
                    return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            cable_attrs.save()
        
        return Response(ProductSerializer(new_subproduct).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['GET'],
    operation_id="retrieve_subproduct",
    description="Recupera los detalles de un subproducto (producto hijo) específico",
    responses={200: ProductSerializer, 404: "SubProduct no encontrado"},
)
@extend_schema(
    methods=['PUT'],
    operation_id="update_subproduct",
    description="Actualiza los detalles de un subproducto (producto hijo) específico",
    request=ProductSerializer,
    responses={200: ProductSerializer, 400: "Solicitud Incorrecta - Datos inválidos"},
)
@extend_schema(
    methods=['DELETE'],
    operation_id="delete_subproduct",
    description="Elimina suavemente un subproducto (producto hijo), estableciendo status en False",
    responses={204: "SubProduct eliminado (soft)", 404: "SubProduct no encontrado"},
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])  # Solo staff update/delete; todos pueden GET
def subproduct_detail(request, product_pk, pk):
    """
    Obtiene, actualiza o elimina suavemente un subproducto específico.
    Un subproducto es un producto con `parent=product_padre`.
    """
    try:
        parent_product = Product.objects.get(pk=product_pk, status=True)
    except Product.DoesNotExist:
        return Response({"detail": "Parent product not found or inactive."}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        subproduct = parent_product.subproducts.get(pk=pk, status=True)
    except Product.DoesNotExist:
        return Response({"detail": "SubProduct not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return retrieve_subproduct(subproduct)
    elif request.method == 'PUT':
        return update_subproduct(request, subproduct)
    elif request.method == 'DELETE':
        return soft_delete_subproduct(subproduct)


def retrieve_subproduct(subproduct):
    """Obtiene los detalles del subproducto utilizando ProductSerializer."""
    serializer = ProductSerializer(subproduct)
    return Response(serializer.data, status=status.HTTP_200_OK)


def update_subproduct(request, subproduct):
    """Actualiza los detalles del subproducto y CableAttributes si el producto es 'Cables'."""
    serializer = ProductSerializer(subproduct, data=request.data, partial=True)
    if serializer.is_valid():
        updated_subproduct = serializer.save()

        # Si la categoría del subproducto es 'Cables', actualizamos o creamos CableAttributes
        if updated_subproduct.category and updated_subproduct.category.name == "Cables":
            cable_attrs, created = CableAttributes.objects.get_or_create(parent=updated_subproduct)
            
            cable_attrs.brand = request.data.get('brand', cable_attrs.brand)
            cable_attrs.number_coil = request.data.get('number_coil', cable_attrs.number_coil)
            cable_attrs.initial_length = request.data.get('initial_length', cable_attrs.initial_length)
            cable_attrs.total_weight = request.data.get('total_weight', cable_attrs.total_weight)
            cable_attrs.coil_weight = request.data.get('coil_weight', cable_attrs.coil_weight)
            
            technical_sheet_photo_b64 = request.data.get('technical_sheet_photo')
            if technical_sheet_photo_b64:
                try:
                    cable_attrs.technical_sheet_photo = decode_image_base64(
                        technical_sheet_photo_b64,
                        updated_subproduct.name
                    )
                except ValueError as e:
                    return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            cable_attrs.save()

        return Response(ProductSerializer(updated_subproduct).data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def soft_delete_subproduct(subproduct):
    """Realiza un soft delete del subproducto, estableciendo `status` a False."""
    subproduct.status = False
    subproduct.save()
    return Response({"detail": "SubProduct set to inactive successfully."}, status=status.HTTP_204_NO_CONTENT)
