import logging
from django.core.exceptions import ValidationError
from django.db import transaction

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.core.pagination import Pagination
from apps.cuts.api.serializers.cutting_order_serializer import CuttingOrderSerializer
from apps.cuts.api.repositories.cutting_order_repository import CuttingOrderRepository
from apps.cuts.docs.cutting_order_doc import (
    list_assigned_cutting_orders_doc,
    list_cutting_orders_doc,
    create_cutting_order_doc,
    get_cutting_order_by_id_doc,
    update_cutting_order_by_id_doc,
    delete_cutting_order_by_id_doc
)
from apps.cuts.tasks import notify_cut_assignment, notify_cut_status_change

logger = logging.getLogger(__name__)


@extend_schema(**list_assigned_cutting_orders_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cutting_order_assigned_list(request):
    """
    Lista las órdenes de corte asignadas al usuario autenticado.
    """
    qs = CuttingOrderRepository.get_cutting_orders_assigned_to(request.user)
    page = Pagination().paginate_queryset(qs, request)
    ser = CuttingOrderSerializer(page, many=True, context={'request': request})
    return Pagination().get_paginated_response(ser.data)


@extend_schema(**list_cutting_orders_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cutting_order_list(request):
    """
    Lista todas las órdenes de corte activas.
    """
    qs = CuttingOrderRepository.get_all_active()
    page = Pagination().paginate_queryset(qs, request)
    ser = CuttingOrderSerializer(page, many=True, context={'request': request})
    return Pagination().get_paginated_response(ser.data)


@extend_schema(**create_cutting_order_doc)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def cutting_order_create(request):
    """
    Crea una orden de corte.
    Solo usuarios staff pueden crear órdenes.
    """
    serializer = CuttingOrderSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = serializer.validated_data
        items = data.pop('items')
        order = CuttingOrderRepository.create(
            customer=data['customer'],
            items=items,
            user_creator=request.user,
            assigned_to=data.get('assigned_to'),
            workflow_status=data.get('workflow_status', 'pending')
        )
        if order.assigned_to:
            notify_cut_assignment.delay(order.assigned_to.id, order.id)
        resp = CuttingOrderSerializer(order, context={'request': request})
        return Response(resp.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error al crear orden de corte: {e}")
        detail = getattr(e, 'detail', str(e))
        code = status.HTTP_400_BAD_REQUEST if isinstance(e, (serializers.ValidationError, ValidationError)) else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response({"detail": detail}, status=code)


@extend_schema(**get_cutting_order_by_id_doc)
@extend_schema(**update_cutting_order_by_id_doc)
@extend_schema(**delete_cutting_order_by_id_doc)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def cutting_order_detail(request, cuts_pk):
    """
    GET    → cualquier usuario autenticado puede ver.
    PUT    → staff puede modificar todo; assigned_to solo puede cambiar workflow_status.
    PATCH  → igual que PUT.
    DELETE → solo staff puede eliminar.
    """
    order = CuttingOrderRepository.get_by_id(cuts_pk)
    if not order:
        return Response({"detail": "Orden de corte no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    # --- GET ---
    if request.method == 'GET':
        ser = CuttingOrderSerializer(order, context={'request': request})
        return Response(ser.data)

    # --- DELETE ---
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({"detail": "Solo staff puede eliminar órdenes."}, status=status.HTTP_403_FORBIDDEN)
        try:
            CuttingOrderRepository.soft_delete_order(order, request.user)
            notify_cut_status_change.delay(order.id, "deleted")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error eliminando orden {cuts_pk}: {e}")
            return Response({"detail": "Error interno al eliminar la orden."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- PUT / PATCH ---
    partial = (request.method == 'PATCH')
    payload = request.data

    is_staff = request.user.is_staff
    is_assigned = (order.assigned_to_id == request.user.id)
    only_workflow = set(payload.keys()) == {"workflow_status"}

    # permiso de edición
    if not (is_staff or (is_assigned and only_workflow)):
        return Response({"detail": "No tienes permiso para modificar esta orden."}, status=status.HTTP_403_FORBIDDEN)

    serializer = CuttingOrderSerializer(order, data=payload, partial=partial, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            data = serializer.validated_data
            items = data.pop('items', None)
            updated = CuttingOrderRepository.update(
                order_instance=order,
                user_modifier=request.user,
                data=data,
                items=items
            )
            notify_cut_status_change.delay(updated.id, updated.workflow_status)
        resp = CuttingOrderSerializer(updated, context={'request': request})
        return Response(resp.data)
    except Exception as e:
        logger.error(f"Error actualizando orden {cuts_pk}: {e}")
        detail = getattr(e, 'detail', str(e))
        code = status.HTTP_400_BAD_REQUEST if isinstance(e, (serializers.ValidationError, ValidationError)) else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response({"detail": detail}, status=code)
