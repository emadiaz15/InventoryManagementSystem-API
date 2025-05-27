from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from apps.products.models.product_model import Product
from apps.products.models.category_model import Category 
from apps.products.models.type_model import Type       


class ProductRepository:
    """
    Repositorio para Product. Delega lógica de save/delete/auditoría a BaseModel.
    El stock se maneja en la app 'stock'.
    """

    @staticmethod
    def get_all_active_products():
        """Obtener todos los productos activos."""
        return Product.objects.filter(status=True).select_related('category', 'type', 'created_by')

    @staticmethod
    def get_by_id(product_id: int) -> Product | None:
        """Obtener un producto activo por su ID."""
        try:
            return Product.objects.select_related('category', 'type', 'created_by').get(id=product_id, status=True)
        except Product.DoesNotExist:
            return None

    @staticmethod
    def create(
        name: str,
        description: str,
        category_id: int,
        type_id: int = None,  # ✅ Ahora opcional
        user=None,
        code: int = None,
        brand: str = None,
        location=None,
        position=None,
        has_subproducts: bool = False
    ) -> Product:
        """
        Crea un nuevo producto usando la lógica de BaseModel.save.
        """
        # 🧱 Verificamos la categoría obligatoria
        try:
            category_instance = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise ValueError(f"La categoría con ID {category_id} no existe.")

        # 🧩 Type es opcional
        type_instance = None
        if type_id is not None:
            try:
                type_instance = Type.objects.get(pk=type_id)
            except Type.DoesNotExist:
                raise ValueError(f"El tipo con ID {type_id} no existe.")

        # 🛠️ Instanciamos el producto
        product_instance = Product(
            name=name,
            description=description,
            category=category_instance,
            type=type_instance,  # ✅ Puede ser None
            code=code,
            brand=brand,
            location=location,
            position=position,
            has_subproducts=has_subproducts
        )
        product_instance.save(user=user)
        return product_instance


    @staticmethod
    def update(
        product_instance: Product,
        user,
        name: str = None,
        description: str = None,
        category_id: int = None,
        type_id: int = None,  # ✅ puede ser None explícitamente
        code: int = None,
        brand: str = None,
        location=None,
        position=None,
        has_subproducts: bool = None
    ) -> Product:
        """
        Actualiza un producto usando la lógica de BaseModel.save.
        """
        changes_made = False

        if name is not None and product_instance.name != name:
            product_instance.name = name; changes_made = True
        if description is not None and product_instance.description != description:
            product_instance.description = description; changes_made = True
        if brand is not None and product_instance.brand != brand:
            product_instance.brand = brand; changes_made = True
        if code is not None and product_instance.code != code:
            product_instance.code = code; changes_made = True
        if location is not None and product_instance.location != location:
            product_instance.location = location; changes_made = True
        if position is not None and product_instance.position != position:
            product_instance.position = position; changes_made = True
        if has_subproducts is not None and product_instance.has_subproducts != has_subproducts:
            product_instance.has_subproducts = has_subproducts; changes_made = True

        # --- 🔁 FK: Categoría (obligatoria) ---
        if category_id is not None and product_instance.category_id != category_id:
            try:
                product_instance.category = Category.objects.get(pk=category_id)
                changes_made = True
            except Category.DoesNotExist:
                raise ValueError(f"La categoría con ID {category_id} no existe.")

        # --- 🔁 FK: Type (opcional) ---
        if product_instance.type_id != type_id:
            if type_id is None:
                product_instance.type = None
                changes_made = True
            else:
                try:
                    product_instance.type = Type.objects.get(pk=type_id)
                    changes_made = True
                except Type.DoesNotExist:
                    raise ValueError(f"El tipo con ID {type_id} no existe.")

        if changes_made:
            product_instance.save(user=user)

        return product_instance

    @staticmethod
    def soft_delete(product_instance: Product, user) -> Product:
        """Realiza un soft delete usando la lógica de BaseModel.delete."""
        if not isinstance(product_instance, Product):
             raise ValueError("Se requiere una instancia de Product válida.")
        product_instance.delete(user=user)
        return product_instance
