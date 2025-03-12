from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from apps.cuts.models.cutting_order_model import CuttingOrder
from apps.stocks.models import SubproductStock
from apps.users.models import User
from apps.products.models.subproduct_model import Subproduct

class CuttingOrderRepository:
    
    @transaction.atomic
    def create_cutting_order(data, user, assigned_to_id):
        """
        Crea una nueva orden de corte asegurando que haya stock suficiente y asignando el usuario adecuado.
        """
        # Validar si el usuario que está creando la orden es staff o no.
        if not user.is_staff:
            raise ValidationError("Solo los usuarios staff pueden crear una orden de corte.")

        subproduct = data.get('subproduct')
        cutting_quantity = data.get('cutting_quantity')

        # Verificar que haya suficiente stock para realizar el corte
        stock = SubproductStock.objects.filter(subproduct=subproduct).order_by('-created_at').first()
        if not stock or stock.quantity < cutting_quantity:
            raise ValidationError(f"No hay suficiente stock para el subproducto {subproduct.name}.")

        # Obtener el usuario al que se asignará la orden usando el ID
        try:
            assigned_to_user = User.objects.get(id=assigned_to_id)
        except User.DoesNotExist:
            raise ValidationError(f"Usuario con ID {assigned_to_id} no encontrado.")
        
        # Crear la orden de corte vinculada a un subproducto
        cutting_order = CuttingOrder(
            subproduct=subproduct,
            customer=data.get('customer'),
            cutting_quantity=cutting_quantity,
            assigned_by=user,  # Asignamos el usuario autenticado
            assigned_to=assigned_to_user,  # Asignamos el usuario correcto
        )

        cutting_order.save(user=user)  # Pasamos el `user` al método `save()`

        return cutting_order


    @staticmethod
    @transaction.atomic
    def update_cutting_order(cutting_order, data, user):
        """
        Actualiza una orden de corte, modificando su estado o cantidad de corte.
        """
        # Validar que solo los usuarios no staff puedan actualizar el estado.
        if not user.is_staff and 'status' not in data:
            raise ValidationError("Solo los usuarios no staff pueden actualizar el estado.")

        new_status = data.get('status', cutting_order.status)
        
        # Si cambia a 'completed', actualizamos stock y validamos
        if new_status == 'completed' and cutting_order.status != 'completed':
            if cutting_order.status != 'in_process':
                raise ValidationError("Cannot complete an order that is not 'in_process'.")
            
            # Completar la orden de corte
            cutting_order.complete_cutting()

            # Actualizamos el estado de la asignación
            cutting_order.assigned_to = cutting_order.assigned_to
            cutting_order.save()
        
        else:
            cutting_order.status = new_status
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
        cutting_order.status = 'completed'  # Aseguramos que se cambue a completada
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
