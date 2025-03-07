from django.utils import timezone

from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct

from apps.stocks.models import Stock

class SubproductRepository:
    @staticmethod
    def get_by_id(subproduct_id: int):
        """Recupera un subproducto por su ID y estado activo"""
        try:
            # Ensure we are getting a subproduct that belongs to a parent product
            subproduct = Product.objects.get(id=subproduct_id, status=True, parent__isnull=False)
            return subproduct
        except Product.DoesNotExist:
            return None

    @staticmethod
    def get_all_active(parent_product_id: int, active=True):
        """Recupera todos los subproductos activos de un producto padre"""
        try:
            parent_product = Product.objects.get(id=parent_product_id, status=True)
            subproducts = parent_product.subproducts.filter(status=active)
            return subproducts
        except Product.DoesNotExist:
            return []

    @staticmethod
    def create(name: str, description: str, parent: Product, user, stock_quantity: int = None):
        """Crea un nuevo subproducto para el producto padre especificado"""
        
        # Creación del subproducto sin necesidad de un 'code'
        subproduct = Product(name=name, description=description, category=parent.category, type=parent.type, parent=parent)
        
        # Guardar el subproducto
        subproduct.save()
        
        # Asignamos el 'created_by' y 'modified_by' directamente si es necesario
        subproduct.created_by = user
        subproduct.modified_by = user
        subproduct.save()

        # Crear el stock si se proporciona la cantidad
        if stock_quantity is not None and stock_quantity >= 0:
            Stock.objects.create(product=subproduct, quantity=stock_quantity, user=user)
        
        # Si la categoría es 'Cables', crear o actualizar los atributos de Subproduct
        if subproduct.category.name == "Cables":
            cable_attrs, created = Subproduct.objects.get_or_create(parent=subproduct)
            cable_attrs.save()

        return subproduct

    @staticmethod
    def update(subproduct_instance: Product, name: str = None, description: str = None, 
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

        # Si la categoría es 'Cables', se crea o actualiza los atributos de Subproduct
        if subproduct_instance.category.name == "Cables":
            cable_attrs, created = Subproduct.objects.get_or_create(parent=subproduct_instance)
            cable_attrs.save()

        return subproduct_instance

    @staticmethod
    def soft_delete(subproduct_instance: Product, user):
        """Realiza un soft delete, estableciendo status a False"""
        subproduct_instance.status = False
        subproduct_instance.deleted_at = timezone.now()
        subproduct_instance.deleted_by = user
        subproduct_instance.save()

        # Eliminar stock relacionado
        Stock.objects.filter(product=subproduct_instance).delete()

        # Si la categoría es 'Cables', eliminamos los atributos de Subproduct
        if subproduct_instance.category.name == "Cables":
            cable_attrs = Subproduct.objects.filter(parent=subproduct_instance).first()
            if cable_attrs:
                cable_attrs.delete()

        return subproduct_instance
