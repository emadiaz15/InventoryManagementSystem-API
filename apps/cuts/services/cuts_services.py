from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal, InvalidOperation

# Models
from apps.cuts.models.cutting_order_model import CuttingOrder, CuttingOrderItem
from apps.cuts.api.repositories.cutting_order_repository import CuttingOrderRepository
from apps.users.models.user_model import User
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.services.stocks_services import (
    check_subproduct_stock,
    dispatch_subproduct_stock_for_cut
)

# --- Servicio para CREAR una Orden de Corte Completa ---
@transaction.atomic
def create_full_cutting_order(
    subproduct_id: int,
    customer: str,
    cutting_quantity: float,
    user_creator: User,
    assigned_to_id: int = None,
    order_number: int = None
) -> CuttingOrder:
    if not user_creator.is_staff:
        raise PermissionDenied("Solo usuarios Staff pueden crear órdenes de corte.")

    if not customer:
        raise ValidationError("El cliente es obligatorio.")
    if order_number is None:
        raise ValidationError("El número de pedido (order_number) es obligatorio.")

    try:
        cutting_quantity_dec = Decimal(str(cutting_quantity))
        if cutting_quantity_dec <= 0:
            raise ValidationError("La cantidad debe ser un número positivo.")
    except InvalidOperation:
        raise ValidationError("Cantidad inválida.")

    subproduct = get_object_or_404(Subproduct, pk=subproduct_id, status=True)
    if not subproduct.parent.has_subproducts:
        raise ValidationError("El producto asociado no permite subproductos.")

    check_subproduct_stock(subproduct=subproduct, quantity_needed=cutting_quantity_dec)

    assigned_to_user = None
    if assigned_to_id:
        assigned_to_user = get_object_or_404(User, pk=assigned_to_id, is_active=True)
        if assigned_to_user.is_staff:
            raise ValidationError("No se puede asignar una orden de corte a un usuario staff.")

    order = CuttingOrder.objects.create(
        order_number=order_number,
        customer=customer,
        created_by=user_creator,
        assigned_to=assigned_to_user,
        workflow_status='pending',
    )

    CuttingOrderItem.objects.create(
        order=order,
        subproduct=subproduct,
        cutting_quantity=cutting_quantity_dec,
        created_by=user_creator
    )

    dispatch_subproduct_stock_for_cut(
        subproduct=subproduct,
        cutting_quantity=cutting_quantity_dec,
        order_pk=order.pk,
        user_performing_cut=user_creator
    )

    return order


# --- Servicio para ASIGNAR una Orden ---
@transaction.atomic
def assign_order_to_operator(order_id: int, operator_id: int, user_assigning: User) -> CuttingOrder:
    if not user_assigning.is_staff:
        raise PermissionDenied("Solo usuarios Staff pueden asignar órdenes.")

    order = CuttingOrderRepository.get_by_id(order_id)
    if not order:
        raise ValidationError(f"Orden de corte ID {order_id} no encontrada o inactiva.")

    if order.workflow_status != 'pending':
        raise ValidationError(f"La orden no se puede asignar en estado '{order.get_workflow_status_display()}'.")

    operator = get_object_or_404(User, pk=operator_id, is_active=True)
    if operator.is_staff:
        raise ValidationError("No se puede asignar una orden a un usuario staff.")

    return CuttingOrderRepository.update_order_fields(
        order,
        user_modifier=user_assigning,
        data={
            'assigned_to': operator,
            'assigned_by': user_assigning
        }
    )


# --- Servicio para COMPLETAR una Orden ---
@transaction.atomic
def complete_order_processing(order_id: int, user_completing: User) -> CuttingOrder:
    order = CuttingOrderRepository.get_by_id(order_id)
    if not order:
        raise ValidationError(f"Orden de corte ID {order_id} no encontrada o inactiva.")

    if not user_completing.is_staff and order.assigned_to != user_completing:
        raise PermissionDenied("No tienes permiso para completar esta orden.")

    return complete_cutting_logic(order, user_completing)


# --- Lógica real de corte (despacho de stock y actualización de estado) ---
@transaction.atomic
def complete_cutting_logic(order: CuttingOrder, user_completing: User) -> CuttingOrder:
    if order.workflow_status != 'in_process':
        raise ValidationError("Debe estar en 'En Proceso' para completarse.")

    if not user_completing or not user_completing.is_authenticated:
        raise ValidationError("Usuario inválido.")

    for item in order.items.select_for_update():
        dispatch_subproduct_stock_for_cut(
            subproduct=item.subproduct,
            cutting_quantity=item.cutting_quantity,
            order_pk=order.pk,
            user_performing_cut=user_completing,
            location=None
        )

    order.workflow_status = 'completed'
    order.completed_at = timezone.now()
    order.save(
        user=user_completing,
        update_fields=['workflow_status', 'completed_at', 'modified_at', 'modified_by']
    )
    return order
