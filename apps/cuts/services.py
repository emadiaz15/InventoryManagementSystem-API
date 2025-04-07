from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist # Añadido ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.conf import settings
import decimal # Para Decimal
# from django.db.models import QuerySet # No se usa QuerySet como type hint aquí explícitamente

# Ajusta rutas de importación
from apps.cuts.models.cutting_order_model import CuttingOrder
# Importamos el REPOSITORIO refactorizado
from apps.cuts.api.repositories.cutting_order_repository import CuttingOrderRepository
# Importamos servicios/modelos necesarios
from apps.stocks.services import dispatch_subproduct_stock_for_cut # , check_subproduct_stock # Asumimos que check_ existe o se implementa
from apps.users.models.user_model import User
from apps.products.models.subproduct_model import Subproduct
# from apps.core.notifications.tasks import send_cutting_order_assigned_email # Tarea Celery

# --- Servicio para CREAR una Orden de Corte Completa ---
@transaction.atomic
def create_full_cutting_order(subproduct_id: int, customer: str, cutting_quantity: float, user_creator: User, assigned_to_id: int = None) -> CuttingOrder:
    """
    Servicio completo para crear una orden de corte:
    1. Verifica permisos del creador.
    2. Valida datos de entrada.
    3. Valida stock disponible (llamando a servicio de stock).
    4. Crea la orden de corte (usando repositorio).
    5. Opcional: Cambia estado inicial o asigna directamente.
    """
    # 1. Verificar Permisos (Ejemplo)
    if not user_creator.is_staff:
        raise PermissionDenied("Solo usuarios Staff pueden crear órdenes de corte.")

    # 2. Validar datos básicos
    try:
        cutting_quantity_dec = decimal.Decimal(str(cutting_quantity)) # Convertir float a Decimal de forma segura
        if cutting_quantity_dec <= 0: raise ValueError("Cantidad debe ser positiva")
    except (ValueError, decimal.InvalidOperation):
        raise ValidationError("La cantidad a cortar debe ser un número positivo válido.")
    if not customer:
         raise ValidationError("El cliente es obligatorio.")

    subproduct = get_object_or_404(Subproduct, pk=subproduct_id, status=True)

    # 3. Validar Stock Disponible (llamando a función/servicio de stock)
    #    Asumimos que check_subproduct_stock existe y lanza ValidationError si no hay
    # try:
    #     check_subproduct_stock(subproduct=subproduct, quantity_needed=cutting_quantity_dec, location=None) # Ajusta si usas ubicaciones
    # except ValidationError as e:
    #     raise ValidationError({'cutting_quantity': e.message if hasattr(e, 'message') else str(e)}) # Asocia error al campo
    # --- Nota: Comentado por ahora si check_subproduct_stock no existe aún ---

    # 4. Procesar asignación (si viene)
    assigned_to_user = None
    if assigned_to_id:
         assigned_to_user = get_object_or_404(User, pk=assigned_to_id, is_active=True)
         if assigned_to_user.is_staff: # Regla de negocio
             raise ValidationError("No se puede asignar una orden de corte a un usuario staff.")

    # 5. Crear la Orden usando el Repositorio
    order = CuttingOrderRepository.create_order(
        subproduct=subproduct,
        customer=customer,
        cutting_quantity=cutting_quantity_dec,
        user_creator=user_creator,
        assigned_by=user_creator, # Creador asigna inicialmente
        assigned_to=assigned_to_user,
        workflow_status='pending' # Siempre pendiente al crear? O depende si se asigna?
    )

    # 6. Opcional: Enviar notificación si se asignó
    # if assigned_to_user:
    #     send_cutting_order_assigned_email.delay(order.id)

    return order


# --- Servicio para ASIGNAR una Orden ---
# La línea 82 tendrá el type hint 'user_assigning: User' correcto
@transaction.atomic
def assign_order_to_operator(order_id: int, operator_id: int, user_assigning: User) -> CuttingOrder:
     """Asigna una orden a un operario y la pone en 'Pendiente'."""
     # 1. Validar Permisos
     if not user_assigning.is_staff:
          raise PermissionDenied("Solo usuarios Staff pueden asignar órdenes.")

     # 2. Obtener Orden y Operario
     order = CuttingOrderRepository.get_by_id(order_id)
     if not order: raise ObjectDoesNotExist(f"Orden de corte ID {order_id} no encontrada o inactiva.")
     if order.workflow_status not in ['pending']: # Solo asignar si está pendiente?
          raise ValidationError(f"La orden {order_id} no se puede asignar en estado '{order.get_workflow_status_display()}'.")

     operator = get_object_or_404(User, pk=operator_id, is_active=True)
     if operator.is_staff:
          raise ValidationError("No se puede asignar una orden de corte a un usuario staff.")

     # 3. Actualizar Orden usando el Repositorio
     update_data = {
         'assigned_to': operator,
         'assigned_by': user_assigning,
         # 'workflow_status': 'pending' # Ya debería estar en pending? O quizás 'assigned'?
     }
     # Pasamos el usuario que modifica para la auditoría de BaseModel.save
     updated_order = CuttingOrderRepository.update_order_fields(order, user_modifier=user_assigning, data=update_data)

     # 4. Enviar Notificación (Celery Task)
     # send_cutting_order_assigned_email.delay(updated_order.id)

     return updated_order

# --- Servicio para COMPLETAR una Orden ---
# La línea 114 tendrá el type hint 'user_completing: User' correcto
@transaction.atomic
def complete_order_processing(order_id: int, user_completing: User) -> CuttingOrder:
     """
     Completa una orden llamando al método del modelo, que a su vez
     llama al servicio de stock.
     """
     # 1. Obtener Orden
     order = CuttingOrderRepository.get_by_id(order_id)
     if not order: raise ObjectDoesNotExist(f"Orden de corte ID {order_id} no encontrada o inactiva.")

     # 2. Validar Permisos (Ejemplo: ¿Solo el asignado o staff?)
     if not user_completing.is_staff and order.assigned_to != user_completing:
          raise PermissionDenied("No tienes permiso para completar esta orden.")

     # 3. Llamar al método del MODELO
     # Este método ya tiene validaciones internas y llama al servicio de stock
     try:
        order.complete_cutting(user_completing=user_completing)
     except ValidationError as e:
          raise ValidationError(e.message if hasattr(e, 'message') else str(e)) # Relanza error de validación

     # 4. Devolver la orden actualizada
     order.refresh_from_db() # Asegura tener los últimos datos post-save
     return order
