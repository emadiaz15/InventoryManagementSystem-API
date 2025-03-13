from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError
from apps.cuts.models.cutting_order_model import CuttingOrder
from apps.cuts.api.repositories.cutting_order_repository import CuttingOrderRepository
from apps.cuts.api.serializers.cutting_order_serializer import CuttingOrderSerializer
from apps.cuts.docs.cutting_order_doc import (
    list_cutting_orders_doc,
    create_cutting_order_doc,
    get_cutting_order_by_id_doc,
    update_cutting_order_by_id_doc,
    delete_cutting_order_by_id_doc
)
from apps.core.pagination import Pagination
from apps.core.notifications.tasks import send_cutting_order_assigned_email

@extend_schema(**list_cutting_orders_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cutting_orders_list_view(request):
    """
    Fetch all cutting orders for the logged-in user. 
    Staff users can view all orders, 
    non-staff users can only view orders assigned to them.
    Excludes orders that have been soft-deleted (i.e., deleted_by is not NULL).
    """
    user = request.user

    # Filtra las órdenes según el estado del usuario (staff o no staff)
    if user.is_staff:
        # Si es staff, mostramos todas las órdenes excepto las eliminadas (deleted_by no es NULL)
        orders = CuttingOrder.objects.exclude(deleted_by__isnull=False)
    else:
        # Si no es staff, mostramos solo las órdenes asignadas al usuario, excepto las eliminadas
        orders = CuttingOrder.objects.filter(assigned_to=user).exclude(deleted_by__isnull=False)

    # Paginación
    page_size = request.query_params.get('page_size', 10)  # Default to 10 if not provided
    paginator = Pagination()
    paginator.page_size = page_size
    paginated_orders = paginator.paginate_queryset(orders, request)

    # Serializa las órdenes paginadas
    serializer = CuttingOrderSerializer(paginated_orders, many=True)

    # Devuelve la respuesta con la paginación
    return paginator.get_paginated_response(serializer.data)



@extend_schema(**create_cutting_order_doc)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cutting_order_create_view(request):
    """
    Vista para crear una nueva orden de corte. Solo disponible para usuarios staff.
    """
    if not request.user.is_staff:
        return Response({"detail": "No tienes permisos para crear órdenes de corte."}, status=status.HTTP_403_FORBIDDEN)

    serializer = CuttingOrderSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        # Crear la orden de corte a través del repositorio
        order = CuttingOrderRepository.create_cutting_order(
            serializer.validated_data,  
            request.user,  
            serializer.validated_data['assigned_to'].id  
        )

        # Enviar correo electrónico de notificación al usuario asignado
        send_cutting_order_assigned_email(order)  # Llamar a la función para enviar el email

        # Retornar la respuesta con los detalles de la orden de corte creada
        return Response(CuttingOrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**get_cutting_order_by_id_doc)
@extend_schema(**update_cutting_order_by_id_doc)
@extend_schema(**delete_cutting_order_by_id_doc)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def cutting_order_detail_view(request, cuts_pk):
    try:
        order = CuttingOrderRepository.get_cutting_order_by_id(cuts_pk)
    except ValidationError:
        return Response({"detail": "Orden de corte no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if request.user.is_staff:
        if request.method == 'GET':
            return retrieve_cutting_order(order)
        elif request.method in ['PUT', 'PATCH']:
            return update_cutting_order(request, order)
        elif request.method == 'DELETE':
            return soft_delete_cutting_order(order)
    else:
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
        if request.user.is_staff:
            order = CuttingOrderRepository.update_cutting_order(order, serializer.validated_data, request.user)
            return Response(CuttingOrderSerializer(order).data, status=status.HTTP_200_OK)
        
        if 'status' in serializer.validated_data:
            if serializer.validated_data['status'] == 'completed':
                return complete_cutting_order(order)
            else:
                order = CuttingOrderRepository.update_cutting_order(order, serializer.validated_data, request.user)
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
