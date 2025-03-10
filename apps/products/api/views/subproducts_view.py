from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.api.repositories.subproduct_repository import SubproductRepository
from apps.products.models.product_model import Product
from apps.products.docs.subproduct_doc import (
    list_subproducts_doc, create_subproduct_doc, get_subproduct_by_id_doc,
    update_product_by_id_doc, delete_product_by_id_doc
)

# ✅ Obtener lista de subproductos con paginación
@extend_schema(**list_subproducts_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def subproduct_list(request, product_pk):
    """Obtiene una lista de subproductos con paginación y filtros"""
    parent_product = get_object_or_404(Product, pk=product_pk, status=True)
    subproducts = SubproductRepository.get_all_active(parent_product.pk)

    paginator = Pagination()
    paginated_subproducts = paginator.paginate_queryset(subproducts, request)
    
    serializer = SubProductSerializer(paginated_subproducts, many=True)
    return paginator.get_paginated_response(serializer.data)


# ✅ Crear un nuevo subproducto
@extend_schema(**create_subproduct_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_subproduct(request, product_pk):
    """Crea un nuevo subproducto asociado a un producto padre"""
    parent_product = get_object_or_404(Product, pk=product_pk, status=True)

    serializer = SubProductSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Validación de stock_quantity para asegurarse de que es un número válido
            stock_quantity = request.data.get('stock_quantity', 0)
            if not isinstance(stock_quantity, int) or stock_quantity < 0:
                return Response({"detail": "La cantidad de stock debe ser un número entero no negativo."}, status=status.HTTP_400_BAD_REQUEST)

            # Crear el subproducto
            new_subproduct = SubproductRepository.create(
                name=serializer.validated_data['name'],
                description=serializer.validated_data['description'],
                parent=parent_product,
                user=request.user,
                stock_quantity=stock_quantity,
            )
            return Response(SubProductSerializer(new_subproduct).data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Obtener, actualizar o eliminar un subproducto
@extend_schema(**get_subproduct_by_id_doc)
@extend_schema(**update_product_by_id_doc)
@extend_schema(**delete_product_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def subproduct_detail(request, product_pk, pk):
    """Obtiene, actualiza o realiza un soft delete de un subproducto"""
    parent_product = get_object_or_404(Product, pk=product_pk, status=True)
    subproduct = SubproductRepository.get_by_id(pk)

    if not subproduct or subproduct.parent != parent_product:
        return Response({"detail": "Subproducto no encontrado o no pertenece al producto padre."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return retrieve_subproduct(subproduct)
    elif request.method == 'PUT':
        return update_subproduct(request, subproduct)
    elif request.method == 'DELETE':
        return soft_delete_subproduct(request, subproduct)


# ✅ Obtener detalles de un subproducto
def retrieve_subproduct(subproduct):
    """Devuelve los detalles de un subproducto"""
    serializer = SubProductSerializer(subproduct)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ✅ Actualizar un subproducto con mejor manejo de errores
def update_subproduct(request, subproduct):
    try:
        serializer = SubProductSerializer(subproduct, data=request.data, partial=True)
        if serializer.is_valid():
            subproduct.modified_by = request.user  # Asigna el usuario que modifica
            subproduct.modified_at = timezone.now()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ✅ Soft delete con mejor manejo de usuario
def soft_delete_subproduct(request, subproduct):
    """Realiza un soft delete del subproducto"""
    subproduct.status = False
    subproduct.deleted_at = timezone.now()
    subproduct.deleted_by = request.user  # Asegura que se asigna el usuario autenticado
    subproduct.save()

    # Eliminar el stock del subproducto si es necesario
    SubproductRepository.soft_delete(subproduct, request.user)

    return Response({"detail": "Subproducto eliminado con éxito."}, status=status.HTTP_204_NO_CONTENT)
