from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.core.pagination import Pagination
from apps.products.api.serializers.type_serializer import TypeSerializer
from apps.products.api.repositories.type_repository import TypeRepository
from apps.products.filters.type_filter import TypeFilter
from apps.products.docs.type_doc import (
    list_type_doc,
    create_type_doc,
    get_type_by_id_doc,
    update_type_by_id_doc,
    delete_type_by_id_doc
)


@extend_schema(**list_type_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def type_list(request):
    """
    Lista todos los tipos activos con paginación y filtros.
    """
    queryset = TypeRepository.get_all_active()
    filterset = TypeFilter(request.GET, queryset=queryset)
    qs = filterset.qs

    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = TypeSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_type_doc)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_type(request):
    """
    Crea un nuevo tipo de producto.
    Solo administradores.
    """
    serializer = TypeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        type_instance = serializer.save(user=request.user)
        return Response(
            TypeSerializer(type_instance, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_type_by_id_doc)
@extend_schema(**update_type_by_id_doc)
@extend_schema(**delete_type_by_id_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def type_detail(request, type_pk):
    """
    GET:  consulta (autenticados).  
    PUT:  actualización (solo administradores).  
    DELETE: baja suave (solo administradores).
    """
    type_instance = TypeRepository.get_by_id(type_pk)
    if not type_instance:
        return Response({"detail": "Tipo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # GET
    if request.method == 'GET':
        serializer = TypeSerializer(type_instance, context={'request': request})
        return Response(serializer.data)

    # PUT
    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para actualizar este tipo."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = TypeSerializer(
            type_instance,
            data=request.data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            updated = serializer.save(user=request.user)
            return Response(TypeSerializer(updated, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE (soft delete)
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response(
                {"detail": "No tienes permiso para eliminar este tipo."},
                status=status.HTTP_403_FORBIDDEN
            )
        TypeRepository.soft_delete(type_instance, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
