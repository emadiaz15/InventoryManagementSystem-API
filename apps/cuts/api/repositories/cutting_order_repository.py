from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models # Para Type Hinting
from typing import Optional, Dict, Any # Para Type Hinting

from apps.cuts.models.cutting_order_model import CuttingOrder 
from apps.users.models import User
from apps.products.models.subproduct_model import Subproduct

class CuttingOrderRepository:
    """
    Repositorio para CuttingOrder. Se enfoca en el acceso básico a datos.
    Delega la lógica de auditoría y soft delete a BaseModel.
    La lógica de negocio compleja (asignar, completar, validar stock) va en servicios.
    """

    @staticmethod
    def get_by_id(order_id: int) -> Optional[CuttingOrder]:
        """
        Obtiene una orden de corte activa por su ID.
        Retorna None si no existe o no está activa.
        """
        try:
            # Usamos select_related para precargar datos relacionados comunes
            return CuttingOrder.objects.select_related(
                'subproduct', 'assigned_by', 'assigned_to', 'created_by'
            ).get(id=order_id, status=True) # status=True es el booleano de BaseModel
        except CuttingOrder.DoesNotExist:
            return None

    @staticmethod
    def get_all_active() -> models.QuerySet[CuttingOrder]:
        """
        Obtiene todas las órdenes de corte activas.
        Ordenadas por defecto por -created_at (de BaseModel.Meta).
        """
        return CuttingOrder.objects.filter(status=True).select_related(
            'subproduct', 'assigned_by', 'assigned_to', 'created_by'
        )

    @staticmethod
    def get_cutting_orders_assigned_to(user: User) -> models.QuerySet[CuttingOrder]:
        """
        Devuelve todas las órdenes de corte activas asignadas a un usuario específico.
        """
        if not isinstance(user, User):
             return CuttingOrder.objects.none()
        # Filtra por usuario asignado y estado activo (booleano)
        return CuttingOrder.objects.filter(assigned_to=user, status=True).select_related(
            'subproduct', 'assigned_by', 'assigned_to', 'created_by'
        )
        # Considera añadir filtro por workflow_status != 'completed' si aplica

    # --- CREATE BÁSICO ---
    @staticmethod
    def create_order(subproduct: Subproduct, customer: str, cutting_quantity: float, user_creator, assigned_by=None, assigned_to=None, workflow_status='pending') -> CuttingOrder:
        """
        Crea una instancia básica de CuttingOrder y la guarda usando BaseModel.save.
        NO realiza validación de stock ni lógica de negocio compleja aquí.
        """
        # Validaciones básicas de entrada (pueden estar también en Serializer/Servicio)
        if not isinstance(subproduct, Subproduct): raise ValueError("Instancia de Subproduct inválida.")
        if not customer: raise ValueError("Cliente requerido.")
        if cutting_quantity <= 0: raise ValueError("Cantidad a cortar debe ser positiva.")
        if not user_creator: raise ValueError("Usuario creador requerido.")

        # Crea instancia con datos proporcionados
        order = CuttingOrder(
            subproduct=subproduct,
            customer=customer,
            cutting_quantity=cutting_quantity,
            workflow_status=workflow_status, # Usa el campo renombrado
            assigned_by=assigned_by,
            assigned_to=assigned_to
        )
        # Delega a BaseModel.save para asignar created_by y guardar
        order.save(user=user_creator)
        return order

    # --- UPDATE BÁSICO ---
    @staticmethod
    def update_order_fields(order_instance: CuttingOrder, user_modifier, data: Dict[str, Any]) -> CuttingOrder:
         """
         Actualiza campos simples de una orden usando BaseModel.save.
         NO maneja cambios de estado complejos, asignaciones o stock.
         'data' debe ser un diccionario con {campo: valor}.
         """
         if not isinstance(order_instance, CuttingOrder): raise ValueError("Instancia inválida.")
         if not user_modifier: raise ValueError("Usuario modificador requerido.")

         changes_made = False
         # Lista de campos permitidos para actualizar via este método básico
         updatable_fields = {'customer', 'cutting_quantity', 'workflow_status', 'assigned_by', 'assigned_to'}

         for field, value in data.items():
              if field in updatable_fields:
                   # Validar el valor si es necesario aquí o en el serializer/servicio
                   if field == 'workflow_status' and value not in dict(CuttingOrder.WORKFLOW_STATUS_CHOICES).keys():
                        raise ValueError(f"Estado de flujo de trabajo inválido: {value}")
                   if getattr(order_instance, field) != value:
                        setattr(order_instance, field, value)
                        changes_made = True

         if changes_made:
              # Delega a BaseModel.save para asignar modified_by/at y guardar
              order_instance.save(user=user_modifier)
         return order_instance


    # --- SOFT DELETE ---
    @staticmethod
    def soft_delete_order(order_instance: CuttingOrder, user_deletor) -> CuttingOrder:
        """Realiza un soft delete usando la lógica de BaseModel.delete."""
        if not isinstance(order_instance, CuttingOrder): raise ValueError("Instancia inválida.")
        if not user_deletor: raise ValueError("Usuario eliminador requerido.")
        order_instance.delete(user=user_deletor) # Delega a BaseModel
        return order_instance

    # Se eliminaron métodos con lógica de negocio compleja (validar stock,
    # asignar con permisos, completar orden, crear eventos de stock, etc.)
    # Esa lógica va en apps/cuts/services.py
