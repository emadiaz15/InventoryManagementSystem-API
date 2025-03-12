from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.cuts.models.cutting_order_model import CuttingOrder
from apps.stocks.models import SubproductStock
from apps.users.models import User
from apps.stocks.models import StockEvent

class CuttingOrderRepository:

    @transaction.atomic
    def create_cutting_order(data, user, assigned_to_id):
        """
        Crea una nueva orden de corte asegurando que haya stock suficiente y asignando el usuario adecuado.
        """
        if not user.is_staff:
            raise ValidationError("Solo los usuarios staff pueden crear una orden de corte.")

        subproduct = data.get('subproduct')
        cutting_quantity = data.get('cutting_quantity')

        # Verificar que haya suficiente stock para realizar el corte
        stock = SubproductStock.objects.filter(subproduct=subproduct).order_by('-created_at').first()
        if not stock or stock.quantity < cutting_quantity:
            raise ValidationError(f"No hay suficiente stock para el subproducto {subproduct.name}.")

        try:
            assigned_to_user = User.objects.get(id=assigned_to_id)
        except User.DoesNotExist:
            raise ValidationError(f"Usuario con ID {assigned_to_id} no encontrado.")
        
        cutting_order = CuttingOrder(
            subproduct=subproduct,
            customer=data.get('customer'),
            cutting_quantity=cutting_quantity,
            assigned_by=user,
            assigned_to=assigned_to_user,
            status='in_process'  # Inicializamos en "in_process"
        )

        # Guardar la orden de corte
        cutting_order.save() 

        # Actualizar el stock (descontar la cantidad)
        stock.quantity -= cutting_quantity
        stock.save()

        # Crear el evento de stock
        StockEvent.objects.create(
            stock_instance=stock,
            quantity_change=-cutting_quantity,
            event_type='salida',
            user=user,
            location=stock.location
        )

        return cutting_order

    @staticmethod
    @transaction.atomic
    def update_cutting_order(cutting_order, data, user):
        """
        Actualiza una orden de corte, modificando su estado o cantidad de corte.
        """
        new_status = data.get('status', cutting_order.status)

        if new_status != cutting_order.status:
            if new_status == 'completed' and cutting_order.status != 'in_process':
                raise ValidationError("No se puede completar una orden que no esté 'en_proceso'.")

        # Si el usuario es staff, puede actualizar cualquier campo
        if new_status == 'completed':
            cutting_order.complete_cutting()  # Llamamos a la lógica de completar la orden y mover el stock

        cutting_order.status = new_status
        cutting_order.modified_by = user
        cutting_order.modified_at = timezone.now()
        cutting_order.save()
        return cutting_order

    @staticmethod
    @transaction.atomic
    def assign_cutting_order(cutting_order, assigned_to_user, user):
        """
        Asigna una orden de corte a un operario (usuario no staff), solo si el usuario es staff.
        """
        if not user.is_staff:
            raise ValidationError("Solo los usuarios staff pueden asignar una orden de corte.")
        
        if assigned_to_user.is_staff:
            raise ValidationError("No se puede asignar una orden de corte a un usuario staff.")
        
        cutting_order.assigned_to = assigned_to_user
        cutting_order.status = 'pending'  # El estado se cambia a pendiente cuando se asigna
        cutting_order.save()
        return cutting_order

    @staticmethod
    @transaction.atomic
    def complete_cutting_order(cutting_order, user):
        """
        Marca la orden de corte como completada y actualiza el stock, solo si el usuario es staff.
        """
        if not user.is_staff:
            raise ValidationError("Solo los usuarios staff pueden completar una orden de corte.")
        
        if cutting_order.status != 'in_process':
            raise ValidationError("La orden debe estar en estado 'in_process' para completarse.")

        cutting_order.complete_cutting()
        cutting_order.status = 'completed'
        cutting_order.completed_at = timezone.now()  # Marcar la fecha de completado
        cutting_order.save()
        return cutting_order

    @staticmethod
    @transaction.atomic
    def delete_cutting_order(cutting_order, user):
        """
        Realiza un soft delete de una orden de corte, solo si el usuario es staff.
        """
        if not user.is_staff:
            raise ValidationError("Solo un usuario staff puede eliminar una orden de corte.")
        
        # Validación: Verificamos si la orden ya está eliminada
        if cutting_order.deleted_at is not None:
            raise ValidationError("La orden ya ha sido eliminada previamente.")
        
        # Asignar el usuario que está realizando el soft delete y la fecha de eliminación
        cutting_order.deleted_at = timezone.now()  # Establece la fecha de eliminación
        cutting_order.deleted_by = user  # Asigna al usuario que está eliminando la orden
        cutting_order.save()  # Guardamos la orden con el soft delete

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
