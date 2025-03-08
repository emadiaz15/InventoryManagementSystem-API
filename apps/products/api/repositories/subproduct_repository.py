from django.utils import timezone
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.models.stock_model import Stock

class SubproductRepository:
    @staticmethod
    def get_by_id(subproduct_id: int):
        """Recupera un subproducto por su ID y estado activo"""
        try:
            subproduct = Subproduct.objects.get(id=subproduct_id, status=True)
            return subproduct
        except Subproduct.DoesNotExist:
            return None  # Puedes considerar lanzar una excepción si prefieres una gestión más explícita

    @staticmethod
    def get_all_active(parent_product_id: int, active=True):
        """Recupera todos los subproductos activos de un producto padre"""
        try:
            parent_product = Product.objects.get(id=parent_product_id, status=True)
            subproducts = parent_product.subproduct_set.filter(status=active)  # Relación inversa de Product
            return subproducts
        except Product.DoesNotExist:
            return []  # O puedes lanzar una excepción, dependiendo de la lógica del negocio

    @staticmethod
    def create(name: str, description: str, parent: Product, user, stock_quantity: int = None):
        """Crea un nuevo subproducto para el producto padre especificado"""
        
        # Creación del subproducto
        subproduct = Subproduct(name=name, description=description, parent=parent)
        subproduct.save()
        
        # Asignamos el 'created_by' y 'modified_by' directamente si es necesario
        subproduct.created_by = user
        subproduct.modified_by = user
        subproduct.save()

        # Validación y creación del stock si es necesario
        if stock_quantity is not None:
            if stock_quantity < 0:
                raise ValueError("La cantidad de stock no puede ser negativa.")
            Stock.objects.create(product=subproduct, quantity=stock_quantity, user=user)

        return subproduct

    @staticmethod
    def update(subproduct_instance: Subproduct, name: str = None, description: str = None,
            status: bool = None, user=None):
        """Actualiza un subproducto existente con los cambios proporcionados"""
        changes_made = False
        
        # Actualizar los campos del subproducto
        if name:
            subproduct_instance.name = name
            changes_made = True
        if description:
            subproduct_instance.description = description
            changes_made = True
        if status is not None:
            subproduct_instance.status = status
            changes_made = True

        # Si se ha realizado algún cambio, se guarda el subproducto
        if user:
            subproduct_instance.modified_by = user

        if changes_made:
            subproduct_instance.modified_at = timezone.now()
            subproduct_instance.save()

        return subproduct_instance

    @staticmethod
    def soft_delete(subproduct_instance: Subproduct, user):
        """Realiza un soft delete, estableciendo status a False"""
        subproduct_instance.status = False
        subproduct_instance.deleted_at = timezone.now()
        subproduct_instance.deleted_by = user
        subproduct_instance.save()

        # Eliminar solo el stock activo relacionado
        Stock.objects.filter(product=subproduct_instance, is_active=True).delete()

        return subproduct_instance
