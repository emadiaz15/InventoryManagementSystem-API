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

# Importar Servicios (AUN NO CREADOS COMPLETAMENTE, PERO LOS LLAMAREMOS)
# from apps.cuts.services import assign_order_to_operator, complete_order_processing # Ejemplos

# Importar Docs
from apps.cuts.docs.cutting_order_doc import (
    list_cutting_orders_doc, create_cutting_order_doc, get_cutting_order_by_id_doc,
    update_cutting_order_by_id_doc, delete_cutting_order_by_id_doc
    # Añade docs para acciones nuevas si las creas
) 

# --- Vista LISTAR (GET) ---
@extend_schema(**list_cutting_orders_doc)
@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly]) # Permite lectura a autenticados, escritura a staff
def cutting_order_list(request):
    """
    Lista órdenes de corte activas (status=True).
    - Staff ve todas.
    - No-Staff ve solo las asignadas a él.
    """
    user = request.user
    if user.is_staff:
        orders_qs = CuttingOrderRepository.get_all_active()
    else:
        orders_qs = CuttingOrderRepository.get_cutting_orders_assigned_to(user)

    # Aplicar otros filtros desde request.query_params si es necesario
    # Ej: workflow_status = request.query_params.get('workflow_status')
    # if workflow_status:
    #     orders_qs = orders_qs.filter(workflow_status=workflow_status)

    paginator = Pagination()
    paginated_orders = paginator.paginate_queryset(orders_qs, request)
    serializer = CuttingOrderSerializer(paginated_orders, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

# --- Vista CREAR (POST) ---
@extend_schema(**create_cutting_order_doc)
@api_view(['POST'])
@permission_classes([IsStaffOrReadAndUpdateOnly]) # SOLO Admin/Staff puede crear órdenes
def cutting_order_create(request):
    """
    Crea una nueva orden de corte.
    La validación de stock y asignación inicial ocurren aquí o en el serializer/servicio.
    La auditoría la maneja BaseSerializer/BaseModel.
    """
    serializer = CuttingOrderSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        try:
            # serializer.save() llama a CuttingOrderSerializer.create -> BaseSerializer.create -> model.save(user=...)
            # La validación de stock está en CuttingOrderSerializer.validate() por ahora.
            # El serializer también asigna assigned_by=user por defecto si no se envía.
            cutting_order_instance = serializer.save(user=request.user)

            # --- LLAMADA A SERVICIO (Opcional aquí, podría ir en señal/task) ---
            # Si la asignación DEBE generar un email inmediato:
            # if cutting_order_instance.assigned_to:
            #     try:
            #         # Idealmente esta lógica estaría en un servicio 'assign_order'
            #         from apps.core.notifications.tasks import send_cutting_order_assigned_email
            #         send_cutting_order_assigned_email.delay(cutting_order_instance.id)
            #     except Exception as email_err:
            #          print(f"ERROR al enviar email para orden {cutting_order_instance.pk}: {email_err}")
            # ---------------------------------------------------------------------

            # Serializa la respuesta
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
@permission_classes([IsStaffOrReadOnly]) # Lectura para todos, escritura solo staff
def cutting_order_detail(request, cuts_pk):
    """
    Obtiene, Actualiza (PUT/PATCH) o Elimina (DELETE - soft) una orden de corte.
    PUT/PATCH actualiza campos básicos. Acciones específicas como 'asignar'
    o 'completar' deberían tener endpoints/servicios dedicados.
    """
    # Obtener instancia usando el repositorio (ya filtra por status=True)
    order = CuttingOrderRepository.get_by_id(cuts_pk)
    if not order:
        return Response({"detail": "Orden de corte no encontrada o inactiva."}, status=status.HTTP_404_NOT_FOUND)

    # Verificar permisos específicos si un no-staff accede
    if not request.user.is_staff and request.method != 'GET' and order.assigned_to != request.user:
         # Un usuario normal solo puede ver (GET) órdenes o interactuar con las SUYAS
         # (y las interacciones PUT/DELETE estándar se bloquean abajo por permiso)
         # Este chequeo es extra por si IsStaffOrReadOnly no fuera suficiente.
         return Response({"detail": "No tienes permiso para modificar/eliminar esta orden."}, status=status.HTTP_403_FORBIDDEN)


    # --- GET ---
    if request.method == 'GET':
        serializer = CuttingOrderSerializer(order, context={'request': request})
        return Response(serializer.data)

    # --- PUT / PATCH ---
    # Actualiza campos básicos definidos en el serializer (customer, quantity, workflow_status, assigned_to, etc.)
    # No ejecuta lógica compleja como 'complete_cutting' aquí.
    elif request.method in ['PUT', 'PATCH']:
        # IsStaffOrReadOnly ya restringe esto a staff, no necesitamos doble check
        # if not request.user.is_staff:
        #     return Response({"detail": "Solo Staff puede modificar órdenes."}, status=status.HTTP_403_FORBIDDEN)

        # Usar partial=True para permitir actualizaciones parciales (PATCH)
        # Si es PUT, el serializer requerirá todos los campos no read-only
        partial = (request.method == 'PATCH')
        serializer = CuttingOrderSerializer(order, data=request.data, context={'request': request}, partial=partial)
        if serializer.is_valid():
             try:
                # Llama a serializer.save() -> BaseSerializer.update -> instance.save(user=...)
                updated_order = serializer.save(user=request.user)
                response_serializer = CuttingOrderSerializer(updated_order, context={'request': request})
                return Response(response_serializer.data)
             except (ValidationError, serializers.ValidationError, ValueError, Exception) as e:
                 print(f"Error al actualizar orden de corte {cuts_pk}: {e}")
                 error_detail = getattr(e, 'detail', str(e)) if isinstance(e, (serializers.ValidationError, ValidationError)) else "Error interno al actualizar."
                 status_code = status.HTTP_400_BAD_REQUEST if isinstance(e, (serializers.ValidationError, ValidationError, ValueError)) else status.HTTP_500_INTERNAL_SERVER_ERROR
                 return Response({"detail": error_detail}, status=status_code)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- DELETE (Soft Delete) ---
    elif request.method == 'DELETE':
        # IsStaffOrReadOnly ya restringe esto a staff
        try:
            # Llama al método delete de BaseModel, pasando el usuario
            order.delete(user=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
             print(f"Error al hacer soft delete de orden {cuts_pk}: {e}")
             return Response({"detail": "Error interno al eliminar la orden."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
