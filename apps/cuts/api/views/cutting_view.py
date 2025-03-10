from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError

from apps.cuts.api.repositories.cutting_order_repository import CuttingOrderRepository
from apps.cuts.api.serializers.cutting_order_serializer import CuttingOrderSerializer
from apps.cuts.docs.cutting_order_doc import (
    list_cutting_orders_doc,
    create_cutting_order_doc,
    get_cutting_order_by_id_doc,
    update_cutting_order_by_id_doc,
    delete_cutting_order_by_id_doc
)


@extend_schema(**list_cutting_orders_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Usar IsAuthenticated para mayor seguridad
def cutting_orders_list_view(request):
    """
    Endpoint para listar todas las órdenes de corte activas.
    """
    orders = CuttingOrderRepository.get_cutting_orders_for_user(request.user)
    serializer = CuttingOrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**create_cutting_order_doc)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cutting_order_create_view(request):
    """
    Endpoint para crear una nueva orden de corte. Verifica el stock antes de crear la orden.
    """
    serializer = CuttingOrderSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        try:
            # ✅ Ahora se usa `subproduct` en lugar de `product`
            order = CuttingOrderRepository.create_cutting_order(serializer.validated_data, request.user)
            return Response(CuttingOrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_409_CONFLICT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_cutting_order_by_id_doc)
@extend_schema(**update_cutting_order_by_id_doc)
@extend_schema(**delete_cutting_order_by_id_doc)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])  # Usar IsAuthenticated para mayor seguridad
def cutting_order_detail_view(request, pk):
    """
    Endpoint para obtener, actualizar o eliminar suavemente una orden de corte específica.
    """
    try:
        order = CuttingOrderRepository.get_cutting_order_by_id(pk)
    except ValidationError:
        return Response({"detail": "Orden de corte no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return retrieve_cutting_order(order)
    elif request.method in ['PUT', 'PATCH']:
        return update_cutting_order(request, order)
    elif request.method == 'DELETE':
        return soft_delete_cutting_order(order)


def retrieve_cutting_order(order):
    """Obtiene los detalles de la orden de corte."""
    serializer = CuttingOrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)


def update_cutting_order(request, order):
    """Actualiza una orden de corte existente."""
    serializer = CuttingOrderSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        # Si el estado es 'completed', intenta completarlo
        if 'status' in serializer.validated_data and serializer.validated_data['status'] == 'completed':
            return complete_cutting_order(order)
        # Si no, realiza la actualización normal
        else:
            order = CuttingOrderRepository.update_cutting_order(order, serializer.validated_data)
            return Response(CuttingOrderSerializer(order).data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def complete_cutting_order(order):
    """Completa una orden de corte y actualiza el stock."""
    try:
        order = CuttingOrderRepository.complete_cutting_order(order)
        return Response(CuttingOrderSerializer(order).data, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def soft_delete_cutting_order(order):
    """Realiza un soft delete de la orden de corte."""
    try:
        CuttingOrderRepository.delete_cutting_order(order, order.assigned_by)
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"detail": "Orden de corte eliminada (soft) correctamente."}, status=status.HTTP_204_NO_CONTENT)
