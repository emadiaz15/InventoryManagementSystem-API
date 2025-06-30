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
from apps.products.models.product_model import Product
from apps.stocks.services.stocks_services import (
    check_subproduct_stock,
    dispatch_subproduct_stock_for_cut
)

# --- Servicio para CREAR una Orden de Corte Completa ---
@transaction.atomic
def create_full_cutting_order(
    product_id: int,
    items: list,
    customer: str,
    user_creator: User,
    assigned_to_id: int = None,
    order_number: int = None,
    operator_can_edit_items: bool = False
) -> CuttingOrder:
    if not user_creator.is_staff:
        raise PermissionDenied("Solo usuarios Staff pueden crear órdenes de corte.")

    if not customer:
        raise ValidationError("El cliente es obligatorio.")
    if order_number is None:
        raise ValidationError("El número de pedido (order_number) es obligatorio.")

    product = get_object_or_404(Product, pk=product_id, status=True)

    if not product.has_subproducts:
        raise ValidationError("El producto no permite subproductos.")

    validated_items = []
    for item in items:
        subproduct = get_object_or_404(Subproduct, pk=item['subproduct_id'], status=True)
        if subproduct.parent_id != product.id:
            raise ValidationError(f"El subproducto {subproduct.pk} no pertenece al producto indicado.")
        try:
            qty = Decimal(str(item['cutting_quantity']))
            if qty <= 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            raise ValidationError("Cantidad inválida en items.")
        check_subproduct_stock(subproduct=subproduct, quantity_needed=qty)
        validated_items.append((subproduct, qty))

    assigned_to_user = None
    if assigned_to_id:
        assigned_to_user = get_object_or_404(User, pk=assigned_to_id, is_active=True)

    order = CuttingOrder.objects.create(
        order_number=order_number,
        customer=customer,
        product=product,
        operator_can_edit_items=operator_can_edit_items,
        created_by=user_creator,
        assigned_to=assigned_to_user,
        workflow_status='pending',
    )

    for sub, qty in validated_items:
        CuttingOrderItem.objects.create(
            order=order,
            subproduct=sub,
            cutting_quantity=qty,
            created_by=user_creator
        )

    for sub, qty in validated_items:
        dispatch_subproduct_stock_for_cut(
            subproduct=sub,
            cutting_quantity=qty,
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

    return CuttingOrderRepository.update(
        order_instance=order,
        user_modifier=user_assigning,
        data={
            'assigned_to': operator
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
