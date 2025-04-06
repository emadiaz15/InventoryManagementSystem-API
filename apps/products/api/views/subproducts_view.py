from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.api.repositories.subproduct_repository import SubproductRepository
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct # Necesario para delete
from apps.products.docs.subproduct_doc import (
    list_subproducts_doc, create_subproduct_doc, get_subproduct_by_id_doc,
    update_product_by_id_doc, # Asumo que este doc es para subproducto update?
    delete_product_by_id_doc # Asumo que este doc es para subproducto delete?
)

@extend_schema(**list_subproducts_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def subproduct_list(request, prod_pk):
    """
    Lista subproductos activos de un producto padre, con paginación.
    Ordenados por defecto por -created_at (de BaseModel).
    """
    # Validar que el producto padre exista y esté activo
    parent_product = get_object_or_404(Product, pk=prod_pk, status=True)
    # Obtener subproductos usando el repositorio (ya ordenados por defecto)
    subproducts = SubproductRepository.get_all_active(parent_product_id=parent_product.pk)

    paginator = Pagination()
    paginated_subproducts = paginator.paginate_queryset(subproducts, request)
    # Pasar contexto al serializador
    serializer = SubProductSerializer(paginated_subproducts, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_subproduct_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_subproduct(request, prod_pk):
    """
    Crea un nuevo subproducto asociado a un producto padre (obtenido de la URL).
    """
    parent_product = get_object_or_404(Product, pk=prod_pk, status=True)

    # Pasamos el parent_product en el contexto para que el serializer lo use
    serializer_context = {
        'request': request,
        'parent_product': parent_product # Añadido para SubProductSerializer.create
    }
    serializer = SubProductSerializer(data=request.data, context=serializer_context)

    if serializer.is_valid():
        try:
            # Llamamos a serializer.save() pasando el usuario.
            # SubProductSerializer.create usará el parent_product del contexto.
            # BaseSerializer.create luego llamará a instance.save(user=...)
            subproduct_instance = serializer.save(user=request.user)
            # Serializar respuesta
            return Response(
                SubProductSerializer(subproduct_instance, context=serializer_context).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e: # Captura errores de la lógica de create del serializer/modelo
             # Loggear el error e idealmente devolver un mensaje más genérico
             print(f"Error al crear subproducto: {e}") # Log
             return Response({"detail": "Error interno al crear el subproducto."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_subproduct_by_id_doc)
@extend_schema(**update_product_by_id_doc) # Revisa nombre del doc
@extend_schema(**delete_product_by_id_doc) # Revisa nombre del doc
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def subproduct_detail(request, prod_pk, subp_pk):
    """
    Obtiene, actualiza o realiza un soft delete de un subproducto específico.
    """
    # Validar padre y obtener subproducto
    parent_product = get_object_or_404(Product, pk=prod_pk, status=True)
    subproduct = SubproductRepository.get_by_id(subp_pk)

    # Validar que exista y pertenezca al padre
    if not subproduct or subproduct.parent_id != parent_product.pk:
        return Response({"detail": "Subproducto no encontrado o no pertenece al producto padre."}, status=status.HTTP_404_NOT_FOUND)

    # --- GET ---
    if request.method == 'GET':
        serializer = SubProductSerializer(subproduct, context={'request': request})
        # Eliminada lógica de comentarios
        return Response(serializer.data)

    # --- PUT ---
    elif request.method == 'PUT':
        serializer = SubProductSerializer(subproduct, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            # Correcto: Llama a serializer.save() pasando el user
            updated_subproduct = serializer.save(user=request.user)
            return Response(SubProductSerializer(updated_subproduct, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- DELETE (Usando el método del Modelo directamente) ---
    elif request.method == 'DELETE':
        try:
            # Llama al método delete de BaseModel, pasando el usuario
            subproduct.delete(user=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
             # Loggear error
             print(f"Error al hacer soft delete de subproducto {subp_pk}: {e}")
             return Response({"detail": "Error interno al eliminar el subproducto."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
