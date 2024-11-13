import os
import django
from faker import Faker

# Establecer la configuración del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings.local')

# Inicializar Django antes de cualquier importación de modelos
django.setup()

from apps.users.models import User
from apps.products.models import Category, Type, Product, Brand
from apps.stocks.models import Stock, StockHistory
from apps.comments.models import Comment
from apps.cuts.models import CuttingOrder
from django.utils.timezone import now
from django.contrib.auth import get_user_model

# Inicializar Faker
fake = Faker()

# Obtener el modelo de Usuario
User = get_user_model()

# Función para generar usuarios falsos
def populate_users(n):
    for _ in range(n):
        username = fake.user_name()
        email = fake.email()
        name = fake.first_name()
        last_name = fake.last_name()
        dni = fake.unique.random_number(digits=8, fix_len=True)
        
        # Crear usuario en la base de datos
        user = User.objects.create_user(
            username=username,
            email=email,
            name=name,
            last_name=last_name,
            password='password123',
            dni=dni,
        )
        print(f'Usuario {user.username} creado con éxito.')

# Función para crear categorías
def create_categories():
    category_names = [
        "Cables", "Conectores", "Transformadores", "Interruptores", 
        "Medidores", "Iluminación", "Protección", "Automatización", 
        "Energía", "Electrónica"
    ]
    categories = []

    for name in category_names:
        # Verificar si ya existe una categoría con este nombre
        category = Category.objects.filter(name=name).first()
        if not category:
            category = Category.objects.create(
                name=name,
                description=f'Descripción de {name}',
                user=User.objects.first()
            )
            print(f'Categoría {category.name} creada con éxito.')
        else:
            print(f'Categoría {category.name} ya existe.')
        
        categories.append(category)

    return categories

# Función para crear tipos
def create_types(category_cables):
    type_names = ["XLPE", "XLC", "PRC", "CCD", "AAD", "XL", "CSC", "CPAA", "AC/CU", "CSA"]
    types = []

    for name in type_names:
        type_ = Type.objects.create(
            name=name,
            description=f'Descripción del tipo {name}',
            category=category_cables,
            user=User.objects.first()
        )
        types.append(type_)
        print(f'Tipo {type_.name} creado con éxito.')

    return types

# Función para crear marcas
def create_brands():
    brand_names = ["BrandA", "BrandB", "BrandC", "BrandD", "BrandE"]
    brands = []

    for name in brand_names:
        brand = Brand.objects.create(
            name=name,
            description=f'Descripción de {name}',
            user=User.objects.first()
        )
        brands.append(brand)
        print(f'Marca {brand.name} creada con éxito.')

    return brands

def create_products(types, categories, brands):
    for _ in range(50):
        # Generar un código único para el producto
        while True:
            product_code = fake.unique.random_int(min=1000, max=9999)
            if not Product.objects.filter(code=product_code).exists():
                break  # Si el código no existe, se sale del bucle
        
        # Crear el producto con el código generado
        product = Product.objects.create(
            name=fake.word(),
            code=product_code,
            type=fake.random_element(types),
            category=fake.random_element(categories),
            brand=fake.random_element(brands),
            description=fake.text(),
            user=User.objects.first(),  # Asigna el primer usuario como dueño de los productos
        )
        print(f'Producto {product.name} con código {product.code} creado con éxito.')


# Función para crear stock inicial para productos
def create_initial_stock_for_products(products):
    user = User.objects.first()
    for product in products:
        initial_quantity = fake.random_number(digits=5, fix_len=False)
        stock_entry = Stock.objects.create(
            product=product,
            quantity=initial_quantity,
            user=user
        )
        print(f'Stock inicial creado para el producto {product.name} con cantidad {initial_quantity}.')

        StockHistory.objects.create(
            product=product,
            stock_before=0,
            stock_after=initial_quantity,
            change_reason="Stock inicial",
            user=user
        )
        print(f'Historial de stock creado para el producto {product.name}.')

# Función para crear comentarios en productos
def create_comments_for_products(products):
    users = User.objects.all()
    for product in products:
        for _ in range(5):
            user = fake.random_element(users) if users.exists() else None
            text = fake.sentence(nb_words=10)

            comment = Comment.objects.create(
                product=product,
                user=user,
                text=text
            )
            print(f'Comentario creado para el producto {product.name} por el usuario {user.username if user else "Anónimo"}.')

def create_cutting_orders(products):
    users = User.objects.all()  # Obtener todos los usuarios existentes
    for _ in range(40):
        product = fake.random_element(products)  # Seleccionar un producto aleatorio
        customer_name = fake.company()  # Nombre del cliente como una empresa ficticia
        
        # Obtener el stock disponible más reciente del producto
        latest_stock = product.stocks.latest('date').quantity
        
        # Ajustar la cantidad de corte al rango permitido
        max_cutting_quantity = min(9999, latest_stock)  # Limitar el valor máximo a 9999 y que no supere el stock
        
        # Generar la cantidad de corte con un límite seguro
        cutting_quantity = fake.pydecimal(
            left_digits=4, right_digits=2, positive=True, 
            min_value=1, max_value=max_cutting_quantity
        )
        
        # Asignar la orden a un usuario aleatorio
        assigned_by = fake.random_element(users)
        operator = fake.random_element(users) if users.exists() else None

        # Crear la orden de corte
        order = CuttingOrder.objects.create(
            product=product,
            customer=customer_name,
            cutting_quantity=cutting_quantity,
            status='pending',  # Estado inicial
            assigned_by=assigned_by,
            operator=operator
        )
        print(f'Orden de corte creada: {order} - Producto: {product.name} - Cliente: {customer_name} - Cantidad: {cutting_quantity}')


if __name__ == '__main__':
    print("Generando 20 usuarios falsos...")
    populate_users(20)
    print("Población de usuarios completada.")

    print("Generando categorías y tipos...")
    categories = create_categories()
    category_cables = Category.objects.filter(name="Cables").first()
    if category_cables:
        types = create_types(category_cables)
        print("Población de tipos completada.")
    else:
        print("No se encontró la categoría 'Cables'.")

    print("Generando marcas...")
    brands = create_brands()

    print("Generando productos...")
    create_products(types, categories, brands)
    print("Población de productos completada.")

    print("Generando stock inicial para los productos...")
    products = Product.objects.all()
    create_initial_stock_for_products(products)
    print("Población de stock completada.")

    print("Generando comentarios para los productos...")
    create_comments_for_products(products)
    print("Población de comentarios completada.")

    print("Generando órdenes de corte...")
    create_cutting_orders(products)
    print("Población de órdenes de corte completada.")
