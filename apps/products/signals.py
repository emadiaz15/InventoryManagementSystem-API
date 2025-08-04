# apps/products/signals.py

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.products.models import Product  # ajusta el import si tu app/model difiere
from apps.products.utils.cache_helpers_products import PRODUCT_LIST_CACHE_PREFIX

@receiver([post_save, post_delete], sender=Product)
def clear_product_list_cache(sender, instance, **kwargs):
    """
    Borra cualquier clave de cache de la lista de productos
    tras crear, actualizar o eliminar un Product.
    """
    pattern = f"*:{PRODUCT_LIST_CACHE_PREFIX}*"
    # django-redis expone delete_pattern en cache
    try:
        deleted = cache.delete_pattern(pattern)
    except AttributeError:
        # si no usas django-redis, puedes usar tu helper delete_keys_by_pattern
        from apps.products.utils.redis_helpers import delete_keys_by_pattern
        deleted = delete_keys_by_pattern(pattern)
    # opcional: loguear cuántas claves borró
    from django.conf import settings
    if settings.DEBUG is False:
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"[Cache] Deleted {deleted} keys matching {pattern}")
