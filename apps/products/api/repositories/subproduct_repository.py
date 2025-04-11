from django.db import transaction, models 
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, ValidationError 

from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from typing import Optional, List, Dict, Any

class SubproductRepository:
    """
    Repositorio para Subproduct. Delega lógica de save/delete/auditoría a BaseModel.
    El stock se maneja en la app 'stock'.
    """

    @staticmethod
    def get_by_id(subproduct_id: int) -> Optional[Subproduct]:
        """Recupera un subproducto activo por su ID."""
        try:
            return Subproduct.objects.select_related('parent', 'created_by').get(id=subproduct_id, status=True)
        except Subproduct.DoesNotExist:
            return None

    @staticmethod
    def get_all_active(parent_product_id: int) -> models.QuerySet[Subproduct]:
        """
        Recupera todos los subproductos activos de un producto padre.
        Orden por defecto (-created_at) viene de BaseModel.Meta.
        """
        return Subproduct.objects.filter(parent_id=parent_product_id, status=True).select_related('parent', 'created_by')

    @staticmethod
    def create(user, parent: Product, **data: Any) -> Subproduct:
        """
        Crea un nuevo subproducto usando la lógica de BaseModel.save.
        Espera el objeto 'parent' y los datos del subproducto en 'data'.
        """
        if not isinstance(parent, Product) or not parent.status:
            raise ValueError("El producto padre no es válido o no está activo.")

        data.pop('quantity', None)

        subproduct_instance = Subproduct(parent=parent, **data)
        subproduct_instance.save(user=user)
        return subproduct_instance

    @staticmethod
    def update(subproduct_instance: Subproduct, user, data: Dict[str, Any]) -> Subproduct:
        """
        Actualiza un subproducto usando la lógica de BaseModel.save.
        Espera un diccionario 'data' con los campos a actualizar.
        """
        changes_made = False
        allowed_fields = {
            'brand', 'number_coil', 'initial_enumeration', 'final_enumeration',
            'gross_weight', 'net_weight', 'initial_stock_quantity',
            'initial_stock_location', 'technical_sheet_photo', 'form_type', 'observations'
        }

        for field, value in data.items():
            if field in allowed_fields:
                if getattr(subproduct_instance, field) != value:
                    setattr(subproduct_instance, field, value)
                    changes_made = True

        if changes_made:
            subproduct_instance.save(user=user)
        return subproduct_instance

    @staticmethod
    def soft_delete(subproduct_instance: Subproduct, user) -> Subproduct:
        """Realiza un soft delete usando la lógica de BaseModel.delete."""
        if not isinstance(subproduct_instance, Subproduct):
            raise ValueError("Se requiere una instancia de Subproduct válida.")
        subproduct_instance.delete(user=user)
        return subproduct_instance
