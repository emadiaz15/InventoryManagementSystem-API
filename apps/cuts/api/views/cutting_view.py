from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
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

# Endpoint para listar todas las órdenes de corte activas
@extend_schema(**list_cutting_orders_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cutting_orders_list_view(request):
    orders = CuttingOrderRepository.get_cutting_orders_for_user(request.user)
    serializer = CuttingOrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**create_cutting_order_doc)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cutting_order_create_view(request):
    """
    Vista para crear una nueva orden de corte. Solo disponible para usuarios staff.
    """
    # Verificar si el usuario es staff
    if not request.user.is_staff:
        return Response({"detail": "No tienes permisos para crear órdenes de corte."}, status=status.HTTP_403_FORBIDDEN)

    serializer = CuttingOrderSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        # Llamamos al repositorio pasándole los datos validados por el serializer
        order = CuttingOrderRepository.create_cutting_order(
            serializer.validated_data,  # Datos validados del serializer
            request.user,  # Usuario autenticado
            serializer.validated_data['assigned_to'].id  # Usamos el ID validado del usuario asignado
        )

        return Response(CuttingOrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_cutting_order_by_id_doc)
@extend_schema(**update_cutting_order_by_id_doc)
@extend_schema(**delete_cutting_order_by_id_doc)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def cutting_order_detail_view(request, pk):
    try:
        order = CuttingOrderRepository.get_cutting_order_by_id(pk)
    except ValidationError:
        return Response({"detail": "Orden de corte no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    # Verificar si el usuario es staff
    if request.user.is_staff:
        # Los usuarios staff pueden realizar todas las acciones
        if request.method == 'GET':
            return retrieve_cutting_order(order)
        elif request.method in ['PUT', 'PATCH']:
            return update_cutting_order(request, order)
        elif request.method == 'DELETE':
            return soft_delete_cutting_order(order)
    else:
        # Los usuarios no staff solo pueden ver la orden y actualizar el estado
        if request.method == 'GET':
            return retrieve_cutting_order(order)
        elif request.method in ['PUT', 'PATCH']:
            if 'status' in request.data:
                return update_cutting_order(request, order)
            else:
                return Response({"detail": "Solo puedes actualizar el estado de la orden."}, status=status.HTTP_400_BAD_REQUEST)
        
    return Response({"detail": "Método no permitido."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Obtiene los detalles de la orden de corte
def retrieve_cutting_order(order):
    serializer = CuttingOrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Actualiza una orden de corte existente
def update_cutting_order(request, order):
    serializer = CuttingOrderSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        # Solo permitimos que los usuarios no staff actualicen el estado
        if 'status' in serializer.validated_data:
            # Si el estado se cambia a 'completed', completamos la orden
            if serializer.validated_data['status'] == 'completed':
                return complete_cutting_order(order)
            else:
                order = CuttingOrderRepository.update_cutting_order(order, serializer.validated_data)
                return Response(CuttingOrderSerializer(order).data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Solo puedes actualizar el estado de la orden."}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Completa una orden de corte y actualiza el stock
def complete_cutting_order(order):
    try:
        order = CuttingOrderRepository.complete_cutting_order(order)
        return Response(CuttingOrderSerializer(order).data, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Realiza un soft delete de la orden de corte
def soft_delete_cutting_order(order):
    try:
        CuttingOrderRepository.delete_cutting_order(order, order.assigned_by)
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"detail": "Orden de corte eliminada (soft) correctamente."}, status=status.HTTP_204_NO_CONTENT)
