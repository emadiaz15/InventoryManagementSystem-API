# fake_db.py

import os
import django
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

from apps.products.models import Category, Type, Product  # Ajusta la ruta según tu proyecto
from apps.cuts.models import CuttingOrder
from apps.comments.models import Comment  # Ajusta si tu Comment está en otra ubicación

fake = Faker()

# ------------------------------------------------------------------------------
# 3. Crear Usuarios
# ------------------------------------------------------------------------------
def create_fake_users(n=5):
    """
    Crea 'n' usuarios falsos utilizando faker.
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
# 5. Crear Tipos
# ------------------------------------------------------------------------------
def create_fake_types(category_cables, n=5):
    """
    Crea 'n' tipos falsos y los asocia a la categoría 'Cables' (o la que se indique).
    """
    types = []
    for _ in range(n):
        name = fake.word().capitalize()  # p.ej. "Utpextra"
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
    """
    products = []
    for _ in range(n):
        # Generar un code único
        while True:
            code = fake.unique.random_int(min=1000, max=9999)
            if not Product.objects.filter(code=code).exists():
                break

        category = fake.random_element(elements=categories)
        type_obj = fake.random_element(elements=types)

        product = Product.objects.create(
            name=fake.word().capitalize(),      # Nombre corto
            code=code,
            description=fake.sentence(nb_words=8),
            image=None,                         # O usa fake.image_url() si deseas
            category=category,                 # Instancia de Category
            type=type_obj,                     # Instancia de Type
            status=True
        )
        print(f'Producto creado: {product.name} (código: {product.code})')
        products.append(product)

    return products

# ------------------------------------------------------------------------------
# 7. Subproductos
# ------------------------------------------------------------------------------
def create_fake_subproducts(parent_product, n=2):
    """
    Crea n subproductos asociados a un product padre específico.
    Depende de cómo manejes la relación en tu modelo de base de datos.
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
            category=parent_product.category,  # misma categoría
            type=parent_product.type,          # mismo tipo
            status=True,
            # Si tu modelo Product tiene un campo 'parent = ForeignKey("self")', podrías usarlo aquí
        )
        print(f'Subproducto creado: {sub.name} (parent: {parent_product.name})')
        subproducts.append(sub)

    return subproducts

# ------------------------------------------------------------------------------
# 8. Crear Comentarios (usando ContentTypes)
# ------------------------------------------------------------------------------
def create_fake_comments(products, n=3):
    """
    Crea 'n' comentarios para cada producto, usando content_type y object_id
    (según tu OpenAPI, donde Comment no tiene campo 'product' directo).
    """
    all_users = list(User.objects.all())
    product_ct = ContentType.objects.get_for_model(Product)  # content_type para Product

    for product in products:
        for _ in range(n):
            user = fake.random_element(elements=all_users) if all_users else None
            text = fake.sentence(nb_words=12)

            if user:
                Comment.objects.create(
                    content_type=product_ct,
                    object_id=product.id,  # ID del producto comentado
                    user=user,
                    text=text
                )
                print(f'Comentario creado en "{product.name}" por {user.username}.')
            else:
                print("No hay usuarios disponibles para crear comentarios.")
                break

# ------------------------------------------------------------------------------
# 9. Crear Órdenes de Corte (CuttingOrder)
# ------------------------------------------------------------------------------
def create_fake_cutting_orders(products, n=10):
    """
    Crea 'n' CuttingOrders, asignando la instancia de User en 'assigned_by'
    y 'assigned_to' (no sus .id).
    """
    all_users = list(User.objects.all())
    status_choices = ["pending", "in_process", "completed"]

    for _ in range(n):
        product = fake.random_element(elements=products)
        customer_name = fake.company()
        cutting_quantity = fake.pydecimal(left_digits=3, right_digits=2, positive=True, min_value=1, max_value=999)

        assigned_by_user = fake.random_element(elements=all_users) if all_users else None
        assigned_to_user = fake.random_element(elements=all_users) if all_users else None

        order = CuttingOrder.objects.create(
            product=product,
            customer=customer_name,
            cutting_quantity=str(cutting_quantity),  # str para campos Decimal o CharField
            status=fake.random_element(elements=status_choices),
            assigned_by=assigned_by_user,  # Se pasa la instancia de User
            assigned_to=assigned_to_user,  # Se pasa la instancia de User
        )
        print(f'Orden de corte creada para {product.name} - Cliente: {customer_name} - Cantidad: {cutting_quantity}')

# ------------------------------------------------------------------------------
# 10. Ejecución principal
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("===== INICIANDO POBLACIÓN DE DATOS FALSOS =====")
    
    # 1. Crear usuarios
    print("\n--- Creando usuarios ---")
    create_fake_users(n=5)
    
    # 2. Crear categorías
    print("\n--- Creando categorías ---")
    categories = create_fake_categories()
    
    # 3. Crear un par de tipos asociado a la categoría 'Cables'
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
    
    # 5. Crear subproductos para los primeros 2 productos (ejemplo)
    print("\n--- Creando subproductos ---")
    if products:
        create_fake_subproducts(products[0], n=2)
        if len(products) > 1:
            create_fake_subproducts(products[1], n=2)
    
    # 6. Crear comentarios en productos
    print("\n--- Creando comentarios ---")
    create_fake_comments(products, n=2)
    
    # 7. Crear órdenes de corte
    print("\n--- Creando órdenes de corte ---")
    create_fake_cutting_orders(products, n=5)
    
    print("\n===== PROCESO DE POBLACIÓN FINALIZADO =====")
