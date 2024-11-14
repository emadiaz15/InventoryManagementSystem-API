# Este archivo define los endpoints para listar, crear, obtener, actualizar y eliminar (de manera suave) subproductos asociados a productos en la API.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from ...models import SubProduct, Product
from ..serializers import SubProductSerializer
from drf_spectacular.utils import extend_schema
import base64
from django.core.files.base import ContentFile

@extend_schema(
    methods=['GET'],
    operation_id="list_subproducts",
    description="Recupera una lista de subproductos para un producto específico",
    parameters=[
        {'name': 'product_pk', 'in': 'path', 'description': 'ID del producto al que pertenecen los subproductos', 'required': True, 'schema': {'type': 'integer'}},
    ],
    responses={200: SubProductSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subproduct_list(request, product_pk):
    """
    Endpoint para listar subproductos de un producto específico.
    """
    # Verifica que el producto exista y esté activo
    try:
        product = Product.objects.get(pk=product_pk, is_active=True)
    except Product.DoesNotExist:
        return Response({"detail": "Producto no encontrado o inactivo."}, status=status.HTTP_404_NOT_FOUND)
    
    # Filtra los subproductos activos asociados al producto
    subproducts = product.subproducts.filter(is_active=True)
    serializer = SubProductSerializer(subproducts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    methods=['POST'],
    operation_id="create_subproduct",
    description="Crea un nuevo subproducto asociado a un producto específico",
    request=SubProductSerializer,
    responses={201: SubProductSerializer, 400: "Solicitud Incorrecta - Datos inválidos"},
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subproduct(request, product_pk):
    """
    Endpoint para crear un nuevo subproducto asociado a un producto específico.
    """
    # Verifica que el producto exista y esté activo
    try:
        product = Product.objects.get(pk=product_pk, is_active=True)
    except Product.DoesNotExist:
        return Response({"detail": "Producto no encontrado o inactivo."}, status=status.HTTP_404_NOT_FOUND)

    serializer = SubProductSerializer(data=request.data)
    if serializer.is_valid():
        # Decodifica la imagen de la ficha técnica si está en Base64 en los datos
        metadata = request.data.get('metadata', {})
        if 'technical_sheet_photo' in metadata:
            try:
                format, imgstr = metadata['technical_sheet_photo'].split(';base64,')
                ext = format.split('/')[-1]
                serializer.validated_data['technical_sheet_photo'] = ContentFile(base64.b64decode(imgstr), name=f"{serializer.validated_data['name']}_tech_sheet.{ext}")
            except Exception as e:
                return Response({"detail": f"Error al decodificar la imagen de la ficha técnica: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Asocia el subproducto al producto y lo guarda
        serializer.save(product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['GET'],
    operation_id="retrieve_subproduct",
    description="Recupera los detalles de un subproducto específico dentro de un producto",
    responses={200: SubProductSerializer, 404: "SubProducto no encontrado"},
)
@extend_schema(
    methods=['PUT'],
    operation_id="update_subproduct",
    description="Actualiza los detalles de un subproducto específico dentro de un producto",
    request=SubProductSerializer,
    responses={200: SubProductSerializer, 400: "Solicitud Incorrecta - Datos inválidos"},
)
@extend_schema(
    methods=['DELETE'],
    operation_id="delete_subproduct",
    description="Elimina suavemente un subproducto específico dentro de un producto, estableciendo is_active en False",
    responses={204: "SubProducto eliminado (soft)", 404: "SubProducto no encontrado"},
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def subproduct_detail(request, product_pk, pk):
    """
    Endpoint para obtener, actualizar o eliminar suavemente un subproducto específico dentro de un producto.
    """
    # Verifica que el producto exista y esté activo
    try:
        product = Product.objects.get(pk=product_pk, is_active=True)
    except Product.DoesNotExist:
        return Response({"detail": "Producto no encontrado o inactivo."}, status=status.HTTP_404_NOT_FOUND)
    
    # Verifica que el subproducto específico exista y esté asociado al producto
    try:
        subproduct = SubProduct.objects.get(pk=pk, product=product)
    except SubProduct.DoesNotExist:
        return Response({"detail": "SubProducto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = SubProductSerializer(subproduct)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = SubProductSerializer(subproduct, data=request.data, partial=True)
        if serializer.is_valid():
            # Decodifica la imagen de la ficha técnica si está en Base64 en los datos
            metadata = request.data.get('metadata', {})
            if 'technical_sheet_photo' in metadata:
                try:
                    format, imgstr = metadata['technical_sheet_photo'].split(';base64,')
                    ext = format.split('/')[-1]
                    serializer.validated_data['technical_sheet_photo'] = ContentFile(base64.b64decode(imgstr), name=f"{serializer.validated_data['name']}_tech_sheet.{ext}")
                except Exception as e:
                    return Response({"detail": f"Error al decodificar la imagen de la ficha técnica: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Marca el subproducto como inactivo en lugar de eliminarlo permanentemente
        subproduct.is_active = False
        subproduct.save()
        return Response({"detail": "SubProducto eliminado (soft) correctamente."}, status=status.HTTP_204_NO_CONTENT)