from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models

from apps.products.models.subproduct_model import Subproduct
from apps.products.models.product_model import Product 
from apps.stocks.models.stock_subproduct_model import SubproductStock 
from typing import Optional, List, Dict, Any

class StockSubproductRepository:
    """
    Repositorio para SubproductStock.
    Delega lógica de save/delete/auditoría a BaseModel.
    La lógica de negocio (ajustar stock + evento) debe estar en un Servicio.
    """

    # --- Métodos de Lectura ---
    @staticmethod
    def get_by_stock_id(stock_id: int) -> Optional[SubproductStock]:
        """Obtiene un registro de stock de subproducto activo por su ID de stock."""
        try:
            # select_related para optimizar
            return SubproductStock.objects.select_related('subproduct', 'created_by', 'modified_by', 'deleted_by').get(id=stock_id, status=True)
        except SubproductStock.DoesNotExist:
            return None

    @staticmethod
    def get_all_active_stocks_for_subproduct(subproduct: Subproduct) -> models.QuerySet[SubproductStock]:
        """Obtiene todos los registros de stock activos para un subproducto específico."""
        if not isinstance(subproduct, Subproduct) or not subproduct.pk:
            return SubproductStock.objects.none() # QuerySet vacío si subproducto no es válido

        return SubproductStock.objects.filter(subproduct=subproduct, status=True).select_related('subproduct', 'created_by')

    @staticmethod
    def get_all_active_stocks_for_product(parent_product: Product) -> models.QuerySet[SubproductStock]:
         """Obtiene todos los stocks activos de los subproductos de un producto padre."""
         if not isinstance(parent_product, Product) or not parent_product.pk:
             return SubproductStock.objects.none()

         return SubproductStock.objects.filter(subproduct__parent=parent_product, status=True).select_related('subproduct', 'created_by')

    # --- Método Create BÁSICO ---
    @staticmethod
    def create_stock(subproduct: Subproduct, quantity: float, user) -> SubproductStock:
        """
        Crea un registro de SubproductStock básico.
        La creación del StockEvent inicial debe manejarse en un Servicio.
        """
        if quantity < 0:
            raise ValueError("La cantidad inicial no puede ser negativa.")
        if not isinstance(subproduct, Subproduct) or subproduct.pk is None:
             raise ValueError("Se requiere una instancia de Subproducto válida.")
        # Validación extra: Asegurar que no exista ya para mismo subproduct/location?
        # if SubproductStock.objects.filter(subproduct=subproduct, location=location).exists():
        #     raise ValidationError(f"Ya existe stock para {subproduct.name} en la ubicación '{location}'. Use ajuste.")

        stock = SubproductStock(
            subproduct=subproduct,
            quantity=quantity
        )
        stock.save(user=user) # Delega a BaseModel
        return stock

    # --- Método Soft Delete ---
    @staticmethod
    def soft_delete_stock(stock_instance: SubproductStock, user) -> SubproductStock:
        """Realiza un soft delete usando la lógica de BaseModel.delete."""
        if not isinstance(stock_instance, SubproductStock):
             raise ValueError("Se requiere una instancia de SubproductStock válida.")
        stock_instance.delete(user=user) # Delega a BaseModel
        return stock_instance

    # --- NO HAY UPDATE GENÉRICO ---
    # Las actualizaciones de cantidad deben hacerse en métodos específicos
    # (ej. adjust_stock, receive_stock, dispatch_stock, complete_cut) en un Servicio o
    # Repositorio que también creen el StockEvent y usen transacciones.
