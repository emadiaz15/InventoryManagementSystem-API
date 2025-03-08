from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination

from apps.products.models.product_model import Product
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer

from apps.products.api.repositories.subproduct_repository import SubproductRepository

from apps.products.docs.subproduct_doc import (
    list_subproducts_doc, create_subproduct_doc, get_subproduct_by_id_doc,
    update_product_by_id_doc, delete_product_by_id_doc
)

@extend_schema(**list_subproducts_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def subproduct_list(request, product_pk):
    """Obtiene una lista de subproductos con paginación y filtros"""
    parent_product = get_object_or_404(Product, pk=product_pk, status=True)  # Obtenemos el producto padre
    subproducts = SubproductRepository.get_all_active(parent_product.pk)
    
    # Paginación
    paginator = Pagination()
    paginated_subproducts = paginator.paginate_queryset(subproducts, request)
    
    # Usamos el serializer de subproductos
    serializer = SubProductSerializer(paginated_subproducts, many=True)
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_subproduct_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_subproduct(request, product_pk):
    """Crea un nuevo subproducto asociado a un producto padre"""
    parent_product = get_object_or_404(Product, pk=product_pk, status=True)  # Obtenemos el producto padre

    # Usamos el serializer para subproductos
    serializer = SubProductSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Creamos el subproducto y lo asociamos con el producto padre
            new_subproduct = SubproductRepository.create(
                name=serializer.validated_data['name'],
                description=serializer.validated_data['description'],
                parent=parent_product,
                user=request.user,
                stock_quantity=request.data.get('stock_quantity', 0),  # Default 0 si no se pasa cantidad
            )
            return Response(SubProductSerializer(new_subproduct).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:  # Captura errores generales
            return Response({"detail": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_subproduct_by_id_doc)
@extend_schema(**update_product_by_id_doc)
@extend_schema(**delete_product_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def subproduct_detail(request, product_pk, pk):
    """Obtiene, actualiza o realiza un soft delete de un subproducto"""
    parent_product = get_object_or_404(Product, pk=product_pk, status=True)  # Obtenemos el producto padre
    subproduct = SubproductRepository.get_by_id(pk)

    if not subproduct or subproduct.parent != parent_product:
        return Response({"detail": "Subproducto no encontrado o no pertenece al producto padre."}, status=status.HTTP_404_NOT_FOUND)

    # Según el método, realizar la acción correspondiente (GET, PUT, DELETE)
    if request.method == 'GET':
        return retrieve_subproduct(subproduct)
    elif request.method == 'PUT':
        return update_subproduct(request, subproduct)
    elif request.method == 'DELETE':
        return soft_delete_subproduct(subproduct)


def retrieve_subproduct(subproduct):
    """Obtiene los detalles del subproducto"""
    serializer = SubProductSerializer(subproduct)
    return Response(serializer.data, status=status.HTTP_200_OK)


def update_subproduct(request, subproduct):
    """Actualiza los detalles de un subproducto"""
    serializer = SubProductSerializer(subproduct, data=request.data, partial=True)
    if serializer.is_valid():
        updated_subproduct = serializer.save(user=request.user)
        return Response(SubProductSerializer(updated_subproduct).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def soft_delete_subproduct(subproduct):
    """Realiza un soft delete de un subproducto"""
    subproduct.status = False
    subproduct.save()

    # Mover la eliminación del stock al repositorio
    SubproductRepository.soft_delete(subproduct, subproduct.modified_by)
    
    return Response({"detail": "Subproducto eliminado con éxito."}, status=status.HTTP_204_NO_CONTENT)
