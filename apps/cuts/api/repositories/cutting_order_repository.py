from typing import Optional, Dict, Any, List
from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.cuts.models.cutting_order_model import CuttingOrder, CuttingOrderItem
from apps.users.models.user_model import User


class CuttingOrderRepository:
    """
    Repositorio para CuttingOrder con ítems.  
    Maneja:
      - get_by_id: precarga assigned_to, created_by y items→subproduct  
      - get_all_active: lo mismo para todos activos  
      - get_assigned_to: filtra por assigned_to  
      - create: crea orden + sus ítems en una sola transacción  
      - update: actualiza campos permitidos + reemplaza ítems  
      - soft_delete: soft‐delete vía BaseModel.delete
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
    def get_all_active() -> models.QuerySet[CuttingOrder]:
        return (
            CuttingOrder.objects
            .filter(status=True)
            .select_related('assigned_to', 'created_by')
            .prefetch_related('items__subproduct')
        )

    @staticmethod
    def get_cutting_orders_assigned_to(user: User) -> models.QuerySet[CuttingOrder]:
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
        customer: str,
        items: List[Dict[str, Any]],
        user_creator,
        assigned_to: Optional[User] = None,
        workflow_status: str = 'pending'
    ) -> CuttingOrder:
        """
        Crea una orden de corte y sus items en una sola transacción.
        items: lista de dicts {'subproduct': Subproduct, 'cutting_quantity': Decimal}
        """
        if not customer:
            raise ValidationError("Cliente requerido.")
        if not user_creator or not getattr(user_creator, 'is_authenticated', False):
            raise ValidationError("Usuario creador inválido.")
        if not items:
            raise ValidationError("Se requiere al menos un item de corte.")

        order = CuttingOrder(
            customer=customer,
            assigned_to=assigned_to,
            workflow_status=workflow_status
        )
        order.save(user=user_creator)

        # Crear cada item
        for itm in items:
            CuttingOrderItem.objects.create(
                order=order,
                subproduct=itm['subproduct'],
                cutting_quantity=itm['cutting_quantity']
            )

        return order

    @staticmethod
    @transaction.atomic
    def update(
        order_instance: CuttingOrder,
        user_modifier,
        data: Dict[str, Any],
        items: Optional[List[Dict[str, Any]]] = None
    ) -> CuttingOrder:
        """
        Actualiza campos permitidos y, si viene 'items', reemplaza la lista de items.
        Campos permitidos en data: customer, workflow_status, assigned_to.
        """
        if not isinstance(order_instance, CuttingOrder):
            raise ValidationError("Instancia de orden inválida.")
        if not user_modifier or not getattr(user_modifier, 'is_authenticated', False):
            raise ValidationError("Usuario modificador inválido.")

        # Actualizar campos de cabecera
        updatable = {'customer', 'workflow_status', 'assigned_to'}
        changed = False
        for field, value in data.items():
            if field in updatable and getattr(order_instance, field) != value:
                setattr(order_instance, field, value)
                changed = True
        if changed:
            order_instance.save(user=user_modifier)

        # Reemplazar items si vienen
        if items is not None:
            # Borramos todos y volvemos a crear
            order_instance.items.all().delete()
            for itm in items:
                CuttingOrderItem.objects.create(
                    order=order_instance,
                    subproduct=itm['subproduct'],
                    cutting_quantity=itm['cutting_quantity']
                )

        return order_instance

    @staticmethod
    def soft_delete(order_instance: CuttingOrder, user_deletor) -> CuttingOrder:
        """
        Soft‐delete de la orden (status=False) usando BaseModel.delete.
        """
        if not isinstance(order_instance, CuttingOrder):
            raise ValidationError("Instancia de orden inválida.")
        if not user_deletor or not getattr(user_deletor, 'is_authenticated', False):
            raise ValidationError("Usuario eliminador inválido.")

        order_instance.delete(user=user_deletor)
        return order_instance
