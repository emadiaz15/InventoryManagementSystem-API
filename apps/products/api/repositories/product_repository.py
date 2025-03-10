from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from apps.products.models.product_model import Product
from apps.stocks.models import ProductStock
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type
from rest_framework.exceptions import ValidationError


class ProductRepository:

    @staticmethod
    def is_code_unique(code, product_id=None):
        """
        Verifica si un código de producto es único.
        Si se está actualizando, ignora el producto actual en la validación.
        """
        query = Product.objects.filter(code=code)
        if product_id:
            query = query.exclude(id=product_id)
        return not query.exists()

    @staticmethod
    def get_by_id(product_id: int):
        """Obtiene un producto por su ID o retorna None si no existe."""
        return Product.objects.filter(id=product_id, status=True).first()

    @staticmethod
    def create(name: str, description: str, category: int, type: int, user, stock_quantity: int = None, code: int = None):
        """Crea un producto nuevo y sugiere un stock inicial si no hay subproductos."""
        
        # Validación de código único
        if code and not ProductRepository.is_code_unique(code):
            raise ValidationError("El código del producto debe ser único.")
        
        # Validar la existencia de la categoría y el tipo usando get_object_or_404
        try:
            category_obj = Category.objects.get(id=category)
        except Category.DoesNotExist:
            raise ValidationError(f"La categoría con ID {category} no existe.")
        
        try:
            type_obj = Type.objects.get(id=type)
        except Type.DoesNotExist:
            raise ValidationError(f"El tipo con ID {type} no existe.")

        # Crear el producto principal
        product = Product(
            name=name,
            description=description,
            category=category_obj,
            type=type_obj,
            code=code,
            created_by=user  # Asignar el usuario que crea el producto
        )
        product.save()

        # Crear stock solo si la cantidad es válida
        if stock_quantity is not None:
            if stock_quantity < 0:
                raise ValidationError("La cantidad de stock no puede ser negativa.")
            ProductStock.objects.create(
                product=product,
                quantity=stock_quantity,
                created_by=user  # Asociar el stock con el usuario que lo crea
            )

        return product

    @staticmethod
    def update(product_instance: Product, name: str = None, description: str = None, 
               category: int = None, type: int = None, status: bool = None, code: int = None, 
               user=None, stock_quantity: int = None):
        """Actualiza los atributos de un producto y el stock si es necesario."""
        changes_made = False

        # Actualizar solo si se pasan los parámetros
        if name and name != product_instance.name:
            product_instance.name = name
            changes_made = True
        if description and description != product_instance.description:
            product_instance.description = description
            changes_made = True
        if category and category != product_instance.category_id:
            try:
                category_obj = Category.objects.get(id=category)
            except ObjectDoesNotExist:
                raise ValueError(f"La categoría con ID {category} no existe.")
            product_instance.category = category_obj
            changes_made = True
        if type and type != product_instance.type_id:
            try:
                type_obj = Type.objects.get(id=type)
            except ObjectDoesNotExist:
                raise ValueError(f"El tipo con ID {type} no existe.")
            product_instance.type = type_obj
            changes_made = True
        if status is not None and status != product_instance.status:
            product_instance.status = status
            changes_made = True
        if code and code != product_instance.code:
            if not ProductRepository.is_code_unique(code, product_instance.id):
                raise ValueError("El código del producto debe ser único.")
            product_instance.code = code
            changes_made = True

        if user:
            product_instance.modified_by = user  # Actualizar el usuario que modificó el producto

        # Guardar solo si hubo cambios
        if changes_made:
            product_instance.modified_at = timezone.now()  # Actualizar la fecha de modificación
            product_instance.save()

        # Si se recibe stock_quantity, actualizamos el stock
        if stock_quantity is not None:
            stock = ProductStock.objects.filter(product=product_instance).first()
            if stock:
                stock.quantity = stock_quantity
                stock.save()
            else:
                # Si no existe stock, lo creamos con la cantidad proporcionada
                ProductStock.objects.create(product=product_instance, quantity=stock_quantity, created_by=user)

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
        return product_instance

    @staticmethod
    def get_all_products():
        """Obtiene todos los productos, independientemente de su estado (activo o inactivo)."""
        return Product.objects.all()

    @staticmethod
    def get_all_active_products():
        """Obtiene todos los productos activos (status=True)."""
        return Product.objects.filter(status=True)
