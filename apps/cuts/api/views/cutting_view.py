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

# --- Listar órdenes de corte asignadas al usuario ---
@extend_schema(
    summary=list_assigned_cutting_orders_doc["summary"],
    description=list_assigned_cutting_orders_doc["description"],
    tags=list_assigned_cutting_orders_doc["tags"],
    operation_id=list_assigned_cutting_orders_doc["operation_id"],
    parameters=list_assigned_cutting_orders_doc["parameters"],
    responses=list_assigned_cutting_orders_doc["responses"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cutting_order_assigned_list(request):
    """
    Endpoint para listar las órdenes de corte asignadas al usuario autenticado.
    """
    qs = CuttingOrderRepository.get_cutting_orders_assigned_to(request.user)

    # 🔁 Igual que en product_list
    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = CuttingOrderSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# --- Listar todas las órdenes de corte ---
@extend_schema(
    summary=list_cutting_orders_doc["summary"],
    description=list_cutting_orders_doc["description"],
    tags=list_cutting_orders_doc["tags"],
    operation_id=list_cutting_orders_doc["operation_id"],
    parameters=list_cutting_orders_doc["parameters"],
    responses=list_cutting_orders_doc["responses"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cutting_order_list(request):
    """
    Endpoint para listar todas las órdenes de corte activas.
    """
    qs = CuttingOrderRepository.get_all_active()

    # 🔁 Consistente con product_list
    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = CuttingOrderSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# --- Crear una nueva orden de corte ---
@extend_schema(
    summary=create_cutting_order_doc["summary"],
    description=create_cutting_order_doc["description"],
    tags=create_cutting_order_doc["tags"],
    operation_id=create_cutting_order_doc["operation_id"],
    request=create_cutting_order_doc["requestBody"],  # Cambiado a `request`
    responses=create_cutting_order_doc["responses"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def cutting_order_create(request):
    """
    Endpoint para crear una nueva orden de corte.
    Solo administradores pueden crear órdenes de corte.
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


# --- Obtener, actualizar y eliminar orden de corte por ID ---
@extend_schema(
    summary=get_cutting_order_by_id_doc["summary"],
    description=get_cutting_order_by_id_doc["description"],
    tags=get_cutting_order_by_id_doc["tags"],
    operation_id=get_cutting_order_by_id_doc["operation_id"],
    parameters=get_cutting_order_by_id_doc["parameters"],
    responses=get_cutting_order_by_id_doc["responses"]
)
@extend_schema(
    summary=update_cutting_order_by_id_doc["summary"],
    description=update_cutting_order_by_id_doc["description"],
    tags=update_cutting_order_by_id_doc["tags"],
    operation_id=update_cutting_order_by_id_doc["operation_id"],
    parameters=update_cutting_order_by_id_doc["parameters"],
    request=update_cutting_order_by_id_doc["requestBody"],  # Cambiado a `request`
    responses=update_cutting_order_by_id_doc["responses"]
)
@extend_schema(
    summary=delete_cutting_order_by_id_doc["summary"],
    description=delete_cutting_order_by_id_doc["description"],
    tags=delete_cutting_order_by_id_doc["tags"],
    operation_id=delete_cutting_order_by_id_doc["operation_id"],
    parameters=delete_cutting_order_by_id_doc["parameters"],
    responses=delete_cutting_order_by_id_doc["responses"]
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def cutting_order_detail(request, cuts_pk):
    """
    Endpoint para:
    - GET: consulta cualquier usuario autenticado puede ver
    - PUT: staff puede modificar todo; assigned_to solo puede cambiar el workflow_status
    - PATCH: igual que PUT
    - DELETE: solo staff puede eliminar
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

    # Permiso de edición
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
