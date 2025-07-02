from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from apps.products.models.product_model import Product
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type
from apps.products.models.subproduct_model import Subproduct

# 🚀 Utilidad común para invalidar patrones
def invalidate_related_cache():
    """
    Invalida las entradas de caché relevantes para productos, categorías, tipos y subproductos.
    """
    cache.delete_pattern("views.decorators.cache.cache*")


# --- Productos ---
@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, **kwargs):
    invalidate_related_cache()


# --- Categorías ---
@receiver([post_save, post_delete], sender=Category)
def invalidate_category_cache(sender, **kwargs):
    invalidate_related_cache()


# --- Tipos ---
@receiver([post_save, post_delete], sender=Type)
def invalidate_type_cache(sender, **kwargs):
    invalidate_related_cache()


# --- Subproductos ---
@receiver([post_save, post_delete], sender=Subproduct)
def invalidate_subproduct_cache(sender, **kwargs):
    invalidate_related_cache()
