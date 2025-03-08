# cutting_order_repository.py
from django.db import transaction
from apps.cuts.models.cutting_order_model import CuttingOrder
from apps.stocks.models.stock_model import Stock
from apps.users.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import now


class CuttingOrderRepository:
    """
    Repositorio para gestionar las operaciones relacionadas con las órdenes de corte.
    """

    @staticmethod
    def create_cutting_order(data, user):
        """
        Crea una nueva orden de corte, asegurándose de que el stock sea suficiente y asignando el usuario adecuado.
        """
        product = data.get('product')
        cutting_quantity = data.get('cutting_quantity')

        # Verificar si hay suficiente stock para crear la orden de corte
        stock = Stock.objects.filter(product=product).latest('created_at')
        if stock.quantity < cutting_quantity:
            raise ValidationError(f"No hay suficiente stock para el producto {product.name}.")

        # Crear la orden de corte
        cutting_order = CuttingOrder.objects.create(
            product=product,
            customer=data.get('customer'),
            cutting_quantity=cutting_quantity,
            assigned_by=user,
        )
        return cutting_order

    @staticmethod
    def update_cutting_order(cutting_order, data):
        """
        Actualiza una orden de corte, cambiando su estado o modificando la cantidad de corte.
        """
        # Si el estado cambia a 'completed', validamos y actualizamos el stock
        new_status = data.get('status', cutting_order.status)
        if new_status == 'completed':
            cutting_order.complete_cutting()
        else:
            cutting_order.status = new_status
            cutting_order.save()

        return cutting_order

    @staticmethod
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
    def complete_cutting_order(cutting_order):
        """
        Marca la orden de corte como completada y actualiza el stock.
        """
        if cutting_order.status != 'in_process':
            raise ValidationError("La orden debe estar en estado 'in_process' para completarse.")

        cutting_order.complete_cutting()
        return cutting_order

    @staticmethod
    def delete_cutting_order(cutting_order, user):
        """
        Elimina (borrado suave) una orden de corte, solo si el usuario es staff.
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
