# fake_generate_subproducts.py

import os
import django
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
from apps.products.models import Product

fake = Faker()

# ------------------------------------------------------------------------------
# 3. Crear Subproductos de Productos Existentes
# ------------------------------------------------------------------------------
def create_fake_subproducts(n_per_product=2):
    """
    Crea subproductos para productos existentes (productos sin 'parent').
    Cada producto recibe hasta 'n_per_product' subproductos.
    """
    parent_products = Product.objects.filter(parent__isnull=True, status=True)

    if not parent_products.exists():
        print("❌ No hay productos disponibles para crear subproductos.")
        return

    subproducts = []
    for parent_product in parent_products:
        for _ in range(n_per_product):
            # Generar un código único
            while True:
                code = fake.unique.random_int(min=1000, max=9999)
                if not Product.objects.filter(code=code).exists():
                    break

            sub = Product.objects.create(
                name=f"{parent_product.name}_sub",
                code=code,
                description=f"Subproducto derivado de {parent_product.name}",
                category=parent_product.category,  # Hereda la categoría
                type=parent_product.type,  # Hereda el tipo
                parent=parent_product,  # Enlaza con el producto padre
                status=True,
            )
            print(f'✅ Subproducto creado: {sub.name} (parent: {parent_product.name}, code: {code})')
            subproducts.append(sub)

    return subproducts

# ------------------------------------------------------------------------------
# 4. EJECUCIÓN PRINCIPAL
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("===== INICIANDO POBLACIÓN DE SUBPRODUCTOS =====")
    create_fake_subproducts(n_per_product=3)  # Ajusta la cantidad de subproductos por producto
    print("\n===== PROCESO DE POBLACIÓN FINALIZADO =====")
