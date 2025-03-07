from django.utils import timezone
from django.shortcuts import get_object_or_404
from apps.products.models.product_model import Product
from apps.stocks.models import Stock
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type

from django.utils import timezone
from apps.products.models.product_model import Product
from apps.stocks.models import Stock
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type

class ProductRepository:
    @staticmethod
    def get_by_id(product_id: int):
        """Obtiene un producto por su ID o retorna None si no existe."""
        try:
            return Product.objects.get(id=product_id, status=True)
        except Product.DoesNotExist:
            return None

    @staticmethod
    def create(name: str, description: str, category: int, type: int, user, stock_quantity: int = None, code: int = None):
        """Crea un producto nuevo y sugiere un stock inicial si no hay subproductos."""
        # Validación de código único
        if code and Product.objects.filter(code=code).exists():
            raise ValueError("El código del producto debe ser único.")
        
        # Crear el producto principal
        category_obj = get_object_or_404(Category, id=category)
        type_obj = get_object_or_404(Type, id=type)

        product = Product(
            name=name,
            description=description,
            category=category_obj,
            type=type_obj,
            code=code,
            created_by=user  # Asignar el usuario que crea el producto
        )
        product.save()

        # Crear stock si es necesario
        if stock_quantity is not None and stock_quantity >= 0:
            Stock.objects.create(
                product=product,
                quantity=stock_quantity,
                user=user  # Asociar el stock con el usuario que lo crea
            )

        return product

    @staticmethod
    def update(product_instance: Product, name: str = None, description: str = None, 
               category: int = None, type: int = None, status: bool = None, code: int = None, user=None, stock_quantity: int = None):
        """Actualiza los atributos de un producto y el stock si es necesario."""
        changes_made = False

        # Actualizar solo si se pasan los parámetros
        if name:
            product_instance.name = name
            changes_made = True
        if description:
            product_instance.description = description
            changes_made = True
        if category:
            product_instance.category = get_object_or_404(Category, id=category)
            changes_made = True
        if type:
            product_instance.type = get_object_or_404(Type, id=type)
            changes_made = True
        if status is not None:
            product_instance.status = status
            changes_made = True
        if code and code != product_instance.code:
            if Product.objects.filter(code=code).exists():
                raise ValueError("El código del producto debe ser único.")
            product_instance.code = code
            changes_made = True

        if user:
            product_instance.modified_by = user  # Actualizar el usuario que modificó el producto

        # Guardar solo si hubo cambios
        if changes_made:
            product_instance.modified_at = timezone.now()  # Actualizar la fecha de modificación
            product_instance.save(user=user)

        # Si se recibe stock_quantity, actualizamos el stock
        if stock_quantity is not None:
            stock = Stock.objects.filter(product=product_instance).first()
            if stock:
                stock.quantity = stock_quantity
                stock.save(user=user)
            else:
                # Si no existe stock, lo creamos con la cantidad proporcionada
                Stock.objects.create(product=product_instance, quantity=stock_quantity, user=user)

        return product_instance

    @staticmethod
    def soft_delete(product_instance: Product, user):
        """
        Realiza un soft delete de un producto, marcándolo como inactivo y
        eliminando su stock relacionado (si es necesario).
        """
        product_instance.status = False
        product_instance.deleted_at = timezone.now()
        product_instance.deleted_by = user
        product_instance.save(update_fields=['status', 'deleted_at', 'deleted_by'])
        product_instance.save()
        return product_instance

    @staticmethod
    def get_all_products():
        """Obtiene todos los productos, independientemente de su estado (activo o inactivo)."""
        return Product.objects.all()

    @staticmethod
    def get_all_active_products():
        """Obtiene todos los productos activos (status=True)."""
        return Product.objects.filter(status=True)
