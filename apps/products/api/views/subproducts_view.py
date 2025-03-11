from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import serializers

from drf_spectacular.utils import extend_schema

from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.users.permissions import IsStaffOrReadOnly
from apps.core.pagination import Pagination
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.api.repositories.subproduct_repository import SubproductRepository
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.products.docs.subproduct_doc import (
    list_subproducts_doc, create_subproduct_doc, get_subproduct_by_id_doc,
    update_product_by_id_doc, delete_product_by_id_doc
)

@extend_schema(**list_subproducts_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def subproduct_list(request, product_pk):
    """
    Vista para listar todos los subproductos activos asociados a un producto padre, con paginación.
    """
    parent_product = get_object_or_404(Product, pk=product_pk, status=True)  # Obtener el producto padre
    subproducts = SubproductRepository.get_all_active(parent_product.pk).order_by('id')  # Listar subproductos activos
    paginator = Pagination()  # Inicializar paginador
    paginated_subproducts = paginator.paginate_queryset(subproducts, request)  # Paginación de subproductos
    serializer = SubProductSerializer(paginated_subproducts, many=True)  # Serializar subproductos
    return paginator.get_paginated_response(serializer.data)  # Responder con los subproductos paginados


@extend_schema(**create_subproduct_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadOnly])
def create_subproduct(request, product_pk):
    """
    Vista para crear un nuevo subproducto asociado a un producto padre.
    El producto padre se obtiene desde la URL del endpoint, no se pasa como parte de la solicitud.
    """
    # Obtener el producto padre como instancia de Product
    parent_product = get_object_or_404(Product, pk=product_pk, status=True)

    # Serializar los datos de entrada
    serializer = SubProductSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        try:
            # Obtener la instancia del usuario autenticado
            user = request.user  # Aquí obtenemos la instancia del usuario autenticado

            # Crear el subproducto y asignar 'created_by' con la instancia de usuario
            new_subproduct = Subproduct.objects.create(
                name=serializer.validated_data['name'],
                description=serializer.validated_data['description'],
                status=serializer.validated_data['status'],
                brand=serializer.validated_data['brand'],
                number_coil=serializer.validated_data['number_coil'],
                initial_length=serializer.validated_data['initial_length'],
                final_length=serializer.validated_data['final_length'],
                total_weight=serializer.validated_data['total_weight'],
                coil_weight=serializer.validated_data['coil_weight'],
                parent=parent_product,  # Relación con el producto padre
                quantity=serializer.validated_data['quantity'],
                created_by=user,  # Asignar la instancia completa de usuario
            )

            # Responder con el subproducto creado
            return Response(
                SubProductSerializer(new_subproduct).data,  # Serializamos el subproducto creado
                status=status.HTTP_201_CREATED  # Código HTTP para creación exitosa
            )

        except ValueError as e:
            print("Error al crear subproducto:", str(e))
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    else:
        # Si la validación falla, imprimimos los errores
        print("Errores de validación:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_subproduct_by_id_doc)
@extend_schema(**update_product_by_id_doc)
@extend_schema(**delete_product_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def subproduct_detail(request, product_pk, pk):
    """
    Vista para obtener, actualizar o realizar un soft delete de un subproducto específico.
    """
    parent_product = get_object_or_404(Product, pk=product_pk, status=True)  # Obtener el producto padre
    subproduct = SubproductRepository.get_by_id(pk)  # Obtener el subproducto por ID

    if not subproduct or subproduct.parent != parent_product:
        # Si no existe o no pertenece al producto padre
        return Response({"detail": "Subproducto no encontrado o no pertenece al producto padre."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Devolver los detalles del subproducto
        return Response(SubProductSerializer(subproduct).data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Actualizar el subproducto
        serializer = SubProductSerializer(subproduct, data=request.data, partial=True)
        if serializer.is_valid():
            user = request.user  # Obtener el usuario autenticado
            # Pasar 'user' al método de actualización
            subproduct = SubproductRepository.update(subproduct, user=user, **serializer.validated_data)
            return Response(SubProductSerializer(subproduct).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Eliminar el subproducto con soft delete
        subproduct = SubproductRepository.soft_delete(subproduct, request.user)
        return Response({"detail": "Subproducto eliminado con éxito."}, status=status.HTTP_204_NO_CONTENT)
