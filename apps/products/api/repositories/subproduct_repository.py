from django.db import transaction # Importar transaction para manejar transacciones
from django.utils import timezone
from django.db import models

from django.core.exceptions import ObjectDoesNotExist
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from typing import Optional, List, Dict, Any # Tipos para type hinting

class SubproductRepository:
    """
    Repositorio para Subproduct. Delega lógica de save/delete/auditoría a BaseModel.
    """

    @staticmethod
    def get_by_id(subproduct_id: int) -> Optional[Subproduct]:
        """Recupera un subproducto activo por su ID."""
        try:
            # Usamos get() que es más directo para PK y maneja DoesNotExist
            return Subproduct.objects.get(id=subproduct_id, status=True)
        except Subproduct.DoesNotExist:
            return None

    @staticmethod
    def get_all_active(parent_product_id: int) -> models.QuerySet[Subproduct]:
        """
        Recupera todos los subproductos activos de un producto padre.
        Orden por defecto (-created_at) viene de BaseModel.Meta.
        """
        return Subproduct.objects.filter(parent_id=parent_product_id, status=True)
        # No añadir .order_by() aquí para usar el default de Meta

    @staticmethod
    def create(user, parent: Product, **data: Any) -> Subproduct:
        """
        Crea un nuevo subproducto usando la lógica de BaseModel.save.
        Espera el objeto 'parent' y los datos del subproducto en 'data'.
        """
        # Validación del padre (se podría omitir si la vista ya lo valida)
        if not isinstance(parent, Product) or not parent.status:
            raise ValueError("El producto padre no es válido o no está activo.")

        # Creamos instancia pasando el padre y el resto de datos
        subproduct_instance = Subproduct(parent=parent, **data)
        # Delega a BaseModel.save para asignar created_by y guardar
        subproduct_instance.save(user=user)
        return subproduct_instance

    @staticmethod
    def update(subproduct_instance: Subproduct, user, data: Dict[str, Any]) -> Subproduct:
        """
        Actualiza un subproducto usando la lógica de BaseModel.save.
        Espera un diccionario 'data' con los campos a actualizar.
        """
        changes_made = False
        allowed_fields = {f.name for f in Subproduct._meta.get_fields()} - \
                         {'id', 'created_at', 'created_by', 'modified_at', 'modified_by', \
                          'deleted_at', 'deleted_by', 'status', 'parent'} # Campos no actualizables aquí

        for field, value in data.items():
            if field in allowed_fields:
                if getattr(subproduct_instance, field) != value:
                    setattr(subproduct_instance, field, value)
                    changes_made = True

        if changes_made:
            subproduct_instance.save(user=user) # Delega a BaseModel.save
        return subproduct_instance

    @staticmethod
    def soft_delete(subproduct_instance: Subproduct, user) -> Subproduct:
        """Realiza un soft delete usando la lógica de BaseModel.delete."""
        subproduct_instance.delete(user=user) # Delega a BaseModel
        return subproduct_instance
