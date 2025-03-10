from django.utils import timezone
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.models import SubproductStock
from typing import Optional, List


class SubproductRepository:

    @staticmethod
    def get_by_id(subproduct_id: int) -> Optional[Subproduct]:
        """Recupera un subproducto por su ID si está activo, retorna None si no existe."""
        return Subproduct.objects.filter(id=subproduct_id, status=True).first()

    @staticmethod
    def get_all_active(parent_product_id: int) -> List[Subproduct]:
        """Recupera todos los subproductos activos de un producto padre."""
        return Subproduct.objects.filter(parent_id=parent_product_id, status=True)

    @staticmethod
    def create(name: str, description: str, parent: Product, user, stock_quantity: Optional[int] = None) -> Subproduct:
        """Crea un nuevo subproducto asociado a un producto padre y opcionalmente su stock."""
        
        if not isinstance(parent, Product):
            raise ValueError("El parámetro 'parent' debe ser una instancia de Product.")

        subproduct = Subproduct(
            name=name, 
            description=description, 
            parent=parent,
            created_by=user,
            modified_by=user
        )
        subproduct.save()

        # Si se proporciona stock_quantity, se crea el stock
        if stock_quantity is not None:
            if stock_quantity < 0:
                raise ValueError("La cantidad de stock no puede ser negativa.")
            SubproductStock.objects.create(product=subproduct, quantity=stock_quantity, created_by=user)

        return subproduct

    @staticmethod
    def update(subproduct_instance: Subproduct, name: Optional[str] = None, 
               description: Optional[str] = None, status: Optional[bool] = None, 
               user: Optional[int] = None) -> Subproduct:
        """Actualiza un subproducto existente con los cambios proporcionados."""
        changes_made = False

        if name and name != subproduct_instance.name:
            subproduct_instance.name = name
            changes_made = True
        if description and description != subproduct_instance.description:
            subproduct_instance.description = description
            changes_made = True
        if status is not None and status != subproduct_instance.status:
            subproduct_instance.status = status
            changes_made = True

        if user:
            subproduct_instance.modified_by = user

        if changes_made:
            subproduct_instance.modified_at = timezone.now()
            subproduct_instance.save()

        return subproduct_instance

    @staticmethod
    def soft_delete(subproduct_instance: Subproduct, user) -> Subproduct:
        """Realiza un soft delete, estableciendo `status=False` y eliminando su stock."""
        subproduct_instance.status = False
        subproduct_instance.deleted_at = timezone.now()
        subproduct_instance.deleted_by = user
        subproduct_instance.save(update_fields=['status', 'deleted_at', 'deleted_by'])

        # Eliminar el stock relacionado solo si está activo
        SubproductStock.objects.filter(product=subproduct_instance, is_active=True).delete()

        return subproduct_instance
