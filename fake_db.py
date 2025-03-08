# fake_db.py

import os
import django
import base64
from django.core.files.base import ContentFile
from faker import Faker

# ------------------------------------------------------------------------------
# 1. Configuración de Django
# ------------------------------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventory_management.settings.local")
django.setup()

# ------------------------------------------------------------------------------
# 2. Importaciones de Django y modelos
# ------------------------------------------------------------------------------
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType  # Para ContentTypes en Comment
from django.utils.timezone import now

User = get_user_model()

from apps.products.models import Category, Type, Product
from apps.cuts.models.cutting_order_model import CuttingOrder
from apps.comments.models.comment_model import Comment
from apps.stocks.models.stock_model import Stock  # Para crear stocks iniciales
from apps.stocks.models.stock_model import StockHistory  # Si deseas poblar historial adicional

fake = Faker()

# ------------------------------------------------------------------------------
# 3. Crear Usuarios
# ------------------------------------------------------------------------------
def create_fake_users(n=5):
    """
    Crea 'n' usuarios falsos utilizando Faker.
    """
    for _ in range(n):
        username = fake.unique.user_name()
        email = fake.unique.email()
        name = fake.first_name()
        last_name = fake.last_name()
        dni = fake.unique.random_number(digits=8, fix_len=True)

        user = User.objects.create_user(
            username=username,
            email=email,
            name=name,
            last_name=last_name,
            password='password123',  # Contraseña fija para pruebas
            dni=dni,
        )
        print(f'Usuario creado: {user.username}')

# ------------------------------------------------------------------------------
# 4. Crear Categorías
# ------------------------------------------------------------------------------
def create_fake_categories():
    """
    Crea un conjunto de categorías base si no existen ya.
    Retorna la lista de instancias Category creadas o existentes.
    """
    category_names = [
        "Cables",
        "Herramientas",
        "Accesorios",
        "Iluminación",
        "Transformadores",
        "Conectores",
        "Automatización",
    ]
    categories = []

    for name in category_names:
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={"description": f"Descripción de {name}", "status": True}
        )
        if created:
            print(f'Categoría creada: {category.name}')
        else:
            print(f'Categoría ya existente: {category.name}')
        categories.append(category)

    return categories

# ------------------------------------------------------------------------------
# 5. Crear Tipos (asociados a la categoría 'Cables')
# ------------------------------------------------------------------------------
def create_fake_types(category_cables, n=5):
    """
    Crea 'n' tipos falsos y los asocia a la categoría 'Cables' (o la que se indique).
    """
    types = []
    for _ in range(n):
        name = fake.word().capitalize()
        type_obj = Type.objects.create(
            name=name,
            description=f"Descripción del tipo {name}",
            category=category_cables,
            status=True
        )
        print(f'Tipo creado: {type_obj.name}')
        types.append(type_obj)
    return types

# ------------------------------------------------------------------------------
# 6. Crear Productos
# ------------------------------------------------------------------------------
def create_fake_products(categories, types, n=10):
    """
    Crea 'n' productos falsos, eligiendo aleatoriamente una Category y un Type.
    Retorna la lista de productos creados.
    """
    products = []
    for _ in range(n):
        # Generar un code único
        while True:
            code = fake.unique.random_int(min=1000, max=9999)
            if not Product.objects.filter(code=code).exists():
                break

        category = fake.random_element(elements=categories)
        type_obj = fake.random_element(elements=types) if types else None

        product = Product.objects.create(
            name=fake.word().capitalize(),
            code=code,
            description=fake.sentence(nb_words=8),
            category=category,   # Instancia de Category
            type=type_obj,       # Instancia de Type
            status=True
        )
        print(f'Producto creado: {product.name} (código: {product.code})')
        products.append(product)

    return products

# ------------------------------------------------------------------------------
# 7. Crear Subproductos
# ------------------------------------------------------------------------------
def create_fake_subproducts(parent_product, n=2):
    """
    Crea n subproductos asociados a un product padre específico.
    Supone que tu modelo Product tiene un campo 'parent = ForeignKey("self")'.
    """
    subproducts = []
    for _ in range(n):
        while True:
            code = fake.unique.random_int(min=1000, max=9999)
            if not Product.objects.filter(code=code).exists():
                break

        sub = Product.objects.create(
            name=f"{parent_product.name}_sub",
            code=code,
            description="Subproducto derivado de " + parent_product.name,
            category=parent_product.category,
            type=parent_product.type,
            parent=parent_product,  # Aquí enlaza con el padre
            status=True,
        )
        print(f'Subproducto creado: {sub.name} (parent: {parent_product.name})')
        subproducts.append(sub)

    return subproducts

# ------------------------------------------------------------------------------
# 8. Crear Comentarios (usando ContentType)
# ------------------------------------------------------------------------------
def create_fake_comments(products, n=3):
    """
    Crea 'n' comentarios para cada producto, usando content_type y object_id.
    """
    all_users = list(User.objects.all())
    product_ct = ContentType.objects.get_for_model(Product)

    for product in products:
        for _ in range(n):
            user = fake.random_element(elements=all_users) if all_users else None
            text = fake.sentence(nb_words=12)

            if user:
                Comment.objects.create(
                    content_type=product_ct,
                    object_id=product.id,
                    user=user,
                    text=text
                )
                print(f'Comentario creado en "{product.name}" por {user.username}.')
            else:
                print("No hay usuarios disponibles para crear comentarios.")
                break

# ------------------------------------------------------------------------------
# 9. Crear Stock inicial
# ------------------------------------------------------------------------------
def create_initial_stock_for_products(products):
    """
    Crea un registro de stock inicial para cada producto, asegurando que
    la validación de CuttingOrder no falle por falta de stock.
    """
    user = User.objects.first()  # Asigna un usuario cualquiera
    for product in products:
        # Verifica si ya existe un stock activo (opcional)
        if not Stock.objects.filter(product=product, is_active=True).exists():
            quantity = fake.random_int(min=10, max=100)
            Stock.objects.create(
                product=product,
                quantity=quantity,
                user=user,
                is_active=True
            )
            print(f"Stock inicial creado para {product.name} con {quantity} unidades.")

# ------------------------------------------------------------------------------
# 10. Crear Órdenes de Corte (CuttingOrder)
# ------------------------------------------------------------------------------
def create_fake_cutting_orders(products, n=10):
    """
    Crea 'n' CuttingOrders, con asignaciones aleatorias de usuario,
    asegurando que cutting_quantity sea un Decimal menor al stock.
    """
    from decimal import Decimal
    all_users = list(User.objects.all())
    status_choices = ["pending", "in_process", "completed"]

    for _ in range(n):
        product = fake.random_element(elements=products)

        # Obtener la cantidad de stock disponible más reciente
        stock_obj = product.stocks.latest('created_at')
        available_stock = stock_obj.quantity

        # Generar un cutting_quantity que no supere el stock actual
        if available_stock < 1:
            # Si no hay stock suficiente ni para 1, omitimos la creación de la orden
            print(f"No hay stock suficiente para generar orden de corte en {product.name}")
            continue

        # Definimos un valor máximo para la orden, p. ej. el stock - 1 o el stock mismo
        max_cut = available_stock if available_stock <= 999 else Decimal("999.00")

        cutting_quantity = fake.pydecimal(
            left_digits=3,
            right_digits=2,
            positive=True,
            min_value=Decimal("1.00"),
            max_value=max_cut
        )

        customer_name = fake.company()
        assigned_by_user = fake.random_element(elements=all_users) if all_users else None
        assigned_to_user = fake.random_element(elements=all_users) if all_users else None

        order = CuttingOrder.objects.create(
            product=product,
            customer=customer_name,
            cutting_quantity=cutting_quantity,  # Pasa un Decimal directamente
            status=fake.random_element(elements=status_choices),
            assigned_by=assigned_by_user,
            assigned_to=assigned_to_user,
        )
        print(f'Orden de corte creada: [Producto: {product.name} | Stock: {available_stock} '
              f'| Cantidad: {cutting_quantity} | Cliente: {customer_name}]')

# ------------------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("===== INICIANDO POBLACIÓN DE DATOS FALSOS =====")

    # 1. Crear usuarios
    print("\n--- Creando usuarios ---")
    create_fake_users(n=5)
    
    # 2. Crear categorías
    print("\n--- Creando categorías ---")
    categories = create_fake_categories()
    
    # 3. Crear Tipos (asociado a la categoría 'Cables', por ejemplo)
    print("\n--- Creando tipos ---")
    category_cables = next((c for c in categories if c.name == "Cables"), None)
    if category_cables:
        types = create_fake_types(category_cables, n=3)
    else:
        types = []
        print("No se encontró la categoría 'Cables'. Se omite creación de tipos.")
    
    # 4. Crear productos
    print("\n--- Creando productos ---")
    products = create_fake_products(categories, types, n=8)
    
    # 5. Crear subproductos (ejemplo) para los primeros 2 productos
    print("\n--- Creando subproductos ---")
    if products:
        create_fake_subproducts(products[0], n=2)
        if len(products) > 1:
            create_fake_subproducts(products[1], n=2)
    
    # 6. Crear comentarios
    print("\n--- Creando comentarios ---")
    create_fake_comments(products, n=2)

    # 7. Crear stock inicial para evitar error de CuttingOrder si no hay stock
    print("\n--- Creando stock inicial para los productos ---")
    create_initial_stock_for_products(products)
    
    # 8. Crear órdenes de corte (CuttingOrder)
    print("\n--- Creando órdenes de corte ---")
    create_fake_cutting_orders(products, n=5)

    print("\n===== PROCESO DE POBLACIÓN FINALIZADO =====")
