from django.db import transaction
from django.utils import timezone
from apps.products.models.product_model import Product
from apps.stocks.models import ProductStock
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type

class ProductRepository:
    """Repositorio para manejar las operaciones de Product."""

    @staticmethod
    def get_all_active_products():
        """
        Obtener todos los productos activos.
        """
        return Product.objects.filter(status=True)

    @staticmethod
    def get_by_id(product_id):
        """
        Obtener un producto por su ID.
        """
        try:
            return Product.objects.get(id=product_id, status=True)
        except Product.DoesNotExist:
            return None

    @staticmethod
    def create(name, description, category_id, type_id, user, code, quantity):
        """
        Crear un nuevo producto.
        """
        with transaction.atomic():
            product = Product.objects.create(
                name=name,
                description=description,
                category_id=category_id,
                type_id=type_id,
                created_by=user,
                code=code,
                quantity=quantity,
                status=True,  # Producto activo por defecto
                created_at=timezone.now()
            )
            return product

    @staticmethod
    def update(product_id, name, description, category_id, type_id, code, quantity, status, user):
        """
        Actualizar un producto existente.
        """
        try:
            # Obtenemos el producto que vamos a actualizar
            product = Product.objects.get(id=product_id, status=True)

            # Solo actualizamos los campos que han cambiado
            updated = False
            if product.name != name:
                product.name = name
                updated = True

            if product.description != description:
                product.description = description
                updated = True

            if product.category_id != category_id:
                product.category_id = category_id
                updated = True

            if product.type_id != type_id:
                product.type_id = type_id
                updated = True

            if product.code != code:
                product.code = code
                updated = True

            if product.quantity != quantity:
                product.quantity = quantity
                updated = True

            if product.status != status:
                product.status = status
                updated = True

            # Si hubo algún cambio en los campos principales, actualizamos los metadatos de modificación
            if updated:
                product.modified_by = user
                product.modified_at = timezone.now()

            # Guardamos el producto actualizado solo si hubo cambios
            if updated:
                product.save()
            return product
        except Product.DoesNotExist:
            return None

    @staticmethod
    def soft_delete(product, user):
        """
        Realiza un soft delete de un producto, marcando su estado como inactivo.
        """
        product.status = False
        product.deleted_by = user
        product.deleted_at = timezone.now()
        product.save()
        return product
