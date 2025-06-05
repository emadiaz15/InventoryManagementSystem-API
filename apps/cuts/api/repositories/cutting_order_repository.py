from typing import Optional, Dict, Any, List
from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.cuts.models.cutting_order_model import CuttingOrder, CuttingOrderItem
from apps.users.models.user_model import User


class CuttingOrderRepository:
    """
    Repositorio para CuttingOrder + items.
    Incluye métodos de acceso, creación, edición y soft-delete.
    """

    @staticmethod
    def get_by_id(order_id: int) -> Optional[CuttingOrder]:
        try:
            return (
                CuttingOrder.objects
                .select_related('assigned_to', 'created_by')
                .prefetch_related('items__subproduct')
                .get(id=order_id, status=True)
            )
        except CuttingOrder.DoesNotExist:
            return None

    @staticmethod
    def get_all_active() -> models.QuerySet:
        return (
            CuttingOrder.objects
            .filter(status=True)
            .select_related('assigned_to', 'created_by')
            .prefetch_related('items__subproduct')
        )

    @staticmethod
    def get_cutting_orders_assigned_to(user: User) -> models.QuerySet:
        if not isinstance(user, User):
            return CuttingOrder.objects.none()
        return (
            CuttingOrder.objects
            .filter(assigned_to=user, status=True)
            .select_related('assigned_to', 'created_by')
            .prefetch_related('items__subproduct')
        )

    @staticmethod
    @transaction.atomic
    def create(
        order_number: int,
        customer: str,
        items: List[Dict[str, Any]],
        user_creator: User,
        assigned_to: Optional[User] = None,
        workflow_status: str = 'pending'
    ) -> CuttingOrder:
        """
        Crea orden de corte + ítems (bulk insert) con validaciones.
        """
        CuttingOrderRepository._validate_create_input(order_number, customer, items, user_creator)

        order = CuttingOrder(
            order_number=order_number,
            customer=customer,
            assigned_to=assigned_to,
            workflow_status=workflow_status
        )
        order.save(user=user_creator)

        item_objs = [
            CuttingOrderItem(
                order=order,
                subproduct=itm['subproduct'],
                cutting_quantity=itm['cutting_quantity']
            ) for itm in items
        ]
        CuttingOrderItem.objects.bulk_create(item_objs)

        return order

    @staticmethod
    @transaction.atomic
    def update(
        order_instance: CuttingOrder,
        user_modifier: User,
        data: Dict[str, Any],
        items: Optional[List[Dict[str, Any]]] = None
    ) -> CuttingOrder:
        """
        Actualiza campos modificables y reemplaza ítems si se pasan.
        """
        if not isinstance(order_instance, CuttingOrder):
            raise ValidationError("Instancia inválida de orden.")
        if not user_modifier or not getattr(user_modifier, 'is_authenticated', False):
            raise ValidationError("Usuario modificador inválido.")

        updatable_fields = {'customer', 'workflow_status', 'assigned_to'}
        changed = False
        for field, value in data.items():
            if field in updatable_fields and getattr(order_instance, field) != value:
                setattr(order_instance, field, value)
                changed = True

        if changed:
            order_instance.save(user=user_modifier)

        if items is not None:
            order_instance.items.all().delete()
            item_objs = [
                CuttingOrderItem(
                    order=order_instance,
                    subproduct=itm['subproduct'],
                    cutting_quantity=itm['cutting_quantity']
                ) for itm in items
            ]
            CuttingOrderItem.objects.bulk_create(item_objs)

        return order_instance

    @staticmethod
    def soft_delete(order_instance: CuttingOrder, user_deletor: User) -> CuttingOrder:
        """
        Marca la orden como inactiva (soft-delete).
        """
        if not isinstance(order_instance, CuttingOrder):
            raise ValidationError("Instancia inválida de orden.")
        if not user_deletor or not getattr(user_deletor, 'is_authenticated', False):
            raise ValidationError("Usuario eliminador inválido.")

        order_instance.delete(user=user_deletor)
        return order_instance

    # =======================================
    # 🔐 Métodos internos
    # =======================================

    @staticmethod
    def _validate_create_input(order_number, customer, items, user_creator):
        if not order_number:
            raise ValidationError("Número de pedido requerido.")
        if not customer:
            raise ValidationError("Cliente requerido.")
        if not user_creator or not getattr(user_creator, 'is_authenticated', False):
            raise ValidationError("Usuario creador inválido.")
        if not items:
            raise ValidationError("Debe incluir al menos un item.")
