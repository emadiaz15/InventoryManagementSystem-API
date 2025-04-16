from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.users.permissions import IsStaffOrReadOnly, IsStaffOrReadAndUpdateOnly
from apps.core.pagination import Pagination
from apps.cuts.api.serializers.cutting_order_serializer import CuttingOrderSerializer
from apps.cuts.api.repositories.cutting_order_repository import CuttingOrderRepository
from apps.cuts.models.cutting_order_model import CuttingOrder
from apps.users.models.user_model import User
from apps.products.models.subproduct_model import Subproduct
from apps.cuts.tasks import notify_cut_assignment, notify_cut_status_change

# Importar Docs
from apps.cuts.docs.cutting_order_doc import (
    list_cutting_orders_doc, create_cutting_order_doc, get_cutting_order_by_id_doc,
    update_cutting_order_by_id_doc, delete_cutting_order_by_id_doc
)

# --- Vista LISTAR (GET) ---
@extend_schema(**list_cutting_orders_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def cutting_order_list(request):
    user = request.user
    if user.is_staff:
        orders_qs = CuttingOrderRepository.get_all_active()
    else:
        orders_qs = CuttingOrderRepository.get_cutting_orders_assigned_to(user)

    paginator = Pagination()
    paginated_orders = paginator.paginate_queryset(orders_qs, request)
    serializer = CuttingOrderSerializer(paginated_orders, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

# --- Vista CREAR (POST) ---
@extend_schema(**create_cutting_order_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadAndUpdateOnly])
def cutting_order_create(request):
    serializer = CuttingOrderSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        try:
            cutting_order_instance = serializer.save(user=request.user)

            # --- Notificación por Celery ---
            if cutting_order_instance.assigned_to:
                notify_cut_assignment.delay(cutting_order_instance.assigned_to.id, cutting_order_instance.id)

            response_serializer = CuttingOrderSerializer(cutting_order_instance, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except (ValidationError, serializers.ValidationError, ValueError, Exception) as e:
            print(f"Error al crear orden de corte: {e}")
            error_detail = getattr(e, 'detail', str(e)) if isinstance(e, serializers.ValidationError) else str(e)
            status_code = status.HTTP_400_BAD_REQUEST if isinstance(e, (serializers.ValidationError, ValidationError, ValueError)) else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response({"detail": error_detail}, status=status_code)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- Vistas de DETALLE (GET, PUT, DELETE) ---
@extend_schema(**get_cutting_order_by_id_doc)
@extend_schema(**update_cutting_order_by_id_doc)
@extend_schema(**delete_cutting_order_by_id_doc)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsStaffOrReadOnly])
def cutting_order_detail(request, cuts_pk):
    order = CuttingOrderRepository.get_by_id(cuts_pk)
    if not order:
        return Response({"detail": "Orden de corte no encontrada o inactiva."}, status=status.HTTP_404_NOT_FOUND)

    if not request.user.is_staff and request.method != 'GET' and order.assigned_to != request.user:
        return Response({"detail": "No tienes permiso para modificar/eliminar esta orden."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = CuttingOrderSerializer(order, context={'request': request})
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        partial = (request.method == 'PATCH')
        serializer = CuttingOrderSerializer(order, data=request.data, context={'request': request}, partial=partial)
        if serializer.is_valid():
            try:
                updated_order = serializer.save(user=request.user)
                notify_cut_status_change.delay(updated_order.id, updated_order.workflow_status)

                response_serializer = CuttingOrderSerializer(updated_order, context={'request': request})
                return Response(response_serializer.data)
            except (ValidationError, serializers.ValidationError, ValueError, Exception) as e:
                print(f"Error al actualizar orden de corte {cuts_pk}: {e}")
                error_detail = getattr(e, 'detail', str(e)) if isinstance(e, (serializers.ValidationError, ValidationError)) else "Error interno al actualizar."
                status_code = status.HTTP_400_BAD_REQUEST if isinstance(e, (serializers.ValidationError, ValidationError, ValueError)) else status.HTTP_500_INTERNAL_SERVER_ERROR
                return Response({"detail": error_detail}, status=status_code)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            order.delete(user=request.user)
            notify_cut_status_change.delay(order.id, "deleted")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"Error al hacer soft delete de orden {cuts_pk}: {e}")
            return Response({"detail": "Error interno al eliminar la orden."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
