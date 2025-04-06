from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from apps.products.models.product_model import Product
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type

class ProductRepository:
    """
    Repositorio para Product. Delega lógica de auditoría/save a BaseModel.
    """

    @staticmethod
    def get_all_active_products():
        """Obtener todos los productos activos."""
        # Orden por defecto (-created_at) viene de BaseModel.Meta
        return Product.objects.filter(status=True).order_by('-created_at')

    @staticmethod
    def get_by_id(product_id: int) -> Product | None:
        """Obtener un producto activo por su ID."""
        try:
            return Product.objects.get(id=product_id, status=True)
        except Product.DoesNotExist:
            return None

    @staticmethod
    def create(name: str, description: str, category_id: int, type_id: int, user, code: int = None, quantity: float = None, brand: str = None, image=None) -> Product:
        """
        Crea un nuevo producto usando la lógica de BaseModel.save.
        """
        try:
            category_instance = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise ValueError(f"La categoría con ID {category_id} no existe.")
        try:
            type_instance = Type.objects.get(pk=type_id)
        except Type.DoesNotExist:
            raise ValueError(f"El tipo con ID {type_id} no existe.")

        # Instancia sin asignar campos de auditoría manualmente
        product_instance = Product(
            name=name,
            description=description,
            category=category_instance, # Pasa instancia
            type=type_instance,       # Pasa instancia
            code=code,
            quantity=quantity,
            brand=brand,
            image=image
            # status es True por defecto en BaseModel
            # created_at es auto_now_add en BaseModel
        )
        # Delega a BaseModel.save para asignar created_by y guardar
        product_instance.save(user=user)
        return product_instance

    # Nota: Considera si realmente necesitas argumentos para todos los campos en update,
    # podrías pasar un diccionario `data` y actualizar solo lo que viene allí.
    # Este ejemplo mantiene la estructura que tenías pero corregida.
    @staticmethod
    def update(product_instance: Product, user, name: str = None, description: str = None, category_id: int = None, type_id: int = None, code: int = None, quantity: float = None, brand: str = None, image=None, status: bool = None) -> Product:
        """
        Actualiza un producto usando la lógica de BaseModel.save.
        Actualiza status SOLO si se pasa explícitamente (para soft delete/reactivate usar métodos dedicados).
        """
        changes_made = False

        # Actualizar campos solo si el valor proporcionado es diferente al actual
        if name is not None and product_instance.name != name:
            product_instance.name = name; changes_made = True
        if description is not None and product_instance.description != description:
            product_instance.description = description; changes_made = True
        if brand is not None and product_instance.brand != brand:
            product_instance.brand = brand; changes_made = True
        if code is not None and product_instance.code != code:
            product_instance.code = code; changes_made = True
        if quantity is not None and product_instance.quantity != quantity:
            product_instance.quantity = quantity; changes_made = True
        if image is not None and product_instance.image != image: # Comparación simple, podría mejorarse
            product_instance.image = image; changes_made = True

        # Manejar FKs
        if category_id is not None and product_instance.category_id != category_id:
            try:
                product_instance.category = Category.objects.get(pk=category_id); changes_made = True
            except Category.DoesNotExist: raise ValueError(f"La categoría con ID {category_id} no existe.")
        if type_id is not None and product_instance.type_id != type_id:
            try:
                product_instance.type = Type.objects.get(pk=type_id); changes_made = True
            except Type.DoesNotExist: raise ValueError(f"El tipo con ID {type_id} no existe.")

        # Manejar status explícitamente (si se pasa)
        # Nota: Para soft delete/reactivate es mejor usar los métodos dedicados
        if status is not None and product_instance.status != status:
             product_instance.status = status
             changes_made = True # Un cambio de status también requiere actualizar modified_*

        # Si hubo cambios, llamar a save pasando el usuario
        if changes_made:
            # transaction.atomic podría ser útil si hay operaciones relacionadas (ej. stock)
            # with transaction.atomic():
            product_instance.save(user=user) # BaseModel.save() asigna modified_*
        return product_instance

    @staticmethod
    def soft_delete(product_instance: Product, user) -> Product:
        """Realiza un soft delete usando la lógica de BaseModel.delete."""
        product_instance.delete(user=user) # Delega a BaseModel
        return product_instance
