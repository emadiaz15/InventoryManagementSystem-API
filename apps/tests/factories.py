from apps.users.models import User
from apps.products.api.repositories.product_repository import ProductRepository
from apps.products.models import Category, Type
from apps.stocks.api.repositories.stock_product_repository import StockProductRepository


def create_user(**kwargs) -> User:
    defaults = {
        'username': 'testuser',
        'email': 'user@example.com',
        'password': 'pass',
        'name': 'Test',
        'last_name': 'User',
        'dni': '1234567890',
    }
    defaults.update(kwargs)
    return User.objects.create_user(
        username=defaults['username'],
        email=defaults['email'],
        password=defaults['password'],
        name=defaults['name'],
        last_name=defaults['last_name'],
        dni=defaults.get('dni'),
    )


def create_category(**kwargs) -> Category:
    defaults = {'name': 'Category', 'description': 'desc'}
    defaults.update(kwargs)
    category = Category(
        name=defaults['name'],
        description=defaults.get('description'),
    )
    category.save(user=defaults.get('user'))
    return category


def create_type(category: Category, **kwargs) -> Type:
    defaults = {'name': 'Type', 'description': 'desc'}
    defaults.update(kwargs)
    type_obj = Type(
        category=category,
        name=defaults['name'],
        description=defaults.get('description'),
    )
    type_obj.save(user=defaults.get('user'))
    return type_obj


def create_product(category: Category, type_obj: Type | None = None, user=None, **kwargs):
    defaults = {'name': 'Product', 'description': 'desc'}
    defaults.update(kwargs)
    return ProductRepository.create(
        name=defaults['name'],
        description=defaults['description'],
        category_id=category.id,
        type_id=type_obj.id if type_obj else None,
        user=user,
    )


def create_product_stock(product, quantity: float = 0, user=None):
    return StockProductRepository.create_stock(product=product, quantity=quantity, user=user)
