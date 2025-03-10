from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from apps.cuts.models.cutting_order_model import CuttingOrder
from apps.stocks.models import SubproductStock
from apps.users.models import User
from apps.products.models.subproduct_model import Subproduct

class CuttingOrderRepository:
    """
    Repositorio para gestionar las operaciones relacionadas con las órdenes de corte.
    """

    @staticmethod
    @transaction.atomic
    def create_cutting_order(data, user):
        """
        Crea una nueva orden de corte asegurando que haya stock suficiente y asignando el usuario adecuado.
        """
        subproduct = data.get('subproduct')  # ✅ Reemplazado 'product' por 'subproduct'
        cutting_quantity = data.get('cutting_quantity')

        # 🔹 Verificar que haya suficiente stock para realizar el corte
        stock = SubproductStock.objects.filter(product=subproduct).latest('created_at')
        if stock.quantity < cutting_quantity:
            raise ValidationError(f"No hay suficiente stock para el subproducto {subproduct.name}.")

        # ✅ Crear la orden de corte vinculada a un subproducto
        cutting_order = CuttingOrder.objects.create(
            subproduct=subproduct,
            customer=data.get('customer'),
            cutting_quantity=cutting_quantity,
            assigned_by=user,
        )
        return cutting_order

    @staticmethod
    @transaction.atomic
    def update_cutting_order(cutting_order, data):
        """
        Actualiza una orden de corte, modificando su estado o cantidad de corte.
        """
        # 🔹 Si cambia a 'completed', actualizamos stock y validamos
        new_status = data.get('status', cutting_order.status)
        
        if new_status == 'completed' and cutting_order.status != 'completed':
            if cutting_order.status != 'in_process':
                raise ValidationError("Cannot complete an order that is not 'in_process'.")
            
            # Completar la orden de corte
            cutting_order.complete_cutting()
        
        else:
            cutting_order.status = new_status
            cutting_order.save()
        
        return cutting_order

    @staticmethod
    @transaction.atomic
    def assign_cutting_order(cutting_order, assigned_to_user):
        """
        Asigna una orden de corte a un operario (usuario no staff).
        """
        if assigned_to_user.is_staff:
            raise ValidationError("No se puede asignar una orden de corte a un usuario staff.")
        
        cutting_order.assigned_to = assigned_to_user
        cutting_order.save()
        return cutting_order

    @staticmethod
    @transaction.atomic
    def complete_cutting_order(cutting_order):
        """
        Marca la orden de corte como completada y actualiza el stock.
        """
        if cutting_order.status != 'in_process':
            raise ValidationError("La orden debe estar en estado 'in_process' para completarse.")

        cutting_order.complete_cutting()
        return cutting_order

    @staticmethod
    @transaction.atomic
    def delete_cutting_order(cutting_order, user):
        """
        Realiza un soft delete de una orden de corte, solo si el usuario es staff.
        """
        if not user.is_staff:
            raise ValidationError("Solo un usuario staff puede eliminar una orden de corte.")
        
        cutting_order.deleted_at = now()
        cutting_order.save()
        return cutting_order

    @staticmethod
    def get_cutting_orders_for_user(user):
        """
        Devuelve todas las órdenes de corte asignadas a un usuario.
        """
        return CuttingOrder.objects.filter(assigned_to=user)

    @staticmethod
    def get_cutting_order_by_id(order_id):
        """
        Obtiene una orden de corte por su ID.
        """
        try:
            return CuttingOrder.objects.get(pk=order_id)
        except CuttingOrder.DoesNotExist:
            raise ValidationError(f"No se encontró la orden de corte con ID {order_id}.")
