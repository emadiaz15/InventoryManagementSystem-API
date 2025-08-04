# apps/products/apps.py

from django.apps import AppConfig

class ProductsConfig(AppConfig):
    name = "apps.products"

    def ready(self):
        # importa el módulo de señales para que se registren
        import apps.products.signals  # noqa
