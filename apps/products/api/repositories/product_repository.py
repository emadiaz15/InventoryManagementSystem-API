from django.utils import timezone
from apps.products.models import Product
from apps.stocks.models import Stock

class ProductRepository:
    @staticmethod
    def get_by_id(product_id: int):
        try:
            return Product.objects.get(id=product_id, status=True)
        except Product.DoesNotExist:
            return None

    @staticmethod
    def get_all_active(category=None, type=None, active=True):
        products = Product.objects.filter(status=active)
        if category:
            products = products.filter(category=category)
        if type:
            products = products.filter(type=type)
        return products

    @staticmethod
    def create(name: str, description: str, category: int, type: int, user, stock_quantity: int = None, code: int = None):
        if code and Product.objects.filter(code=code).exists():
            raise ValueError("El código del producto debe ser único.")
        
        product = Product(name=name, description=description, category=category, type=type, code=code)
        product.save(user=user)
        
        if stock_quantity is not None and stock_quantity >= 0:
            Stock.objects.create(product=product, quantity=stock_quantity, user=user)
        
        return product

    @staticmethod
    def update(product_instance: Product, name: str = None, description: str = None, 
               category: int = None, type: int = None, status: bool = None, code: int = None, user=None):
        changes_made = False
        if name:
            product_instance.name = name
            changes_made = True
        if description:
            product_instance.description = description
            changes_made = True
        if category:
            product_instance.category = category
            changes_made = True
        if type:
            product_instance.type = type
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
            product_instance.modified_by = user

        if changes_made:
            product_instance.modified_at = timezone.now()
            product_instance.save(user=user)

        return product_instance

    @staticmethod
    def soft_delete(product_instance: Product, user):
        product_instance.status = False
        product_instance.deleted_at = timezone.now()
        product_instance.deleted_by = user
        product_instance.save(user=user)

        # Eliminar stock relacionado
        Stock.objects.filter(product=product_instance).delete()

        return product_instance
