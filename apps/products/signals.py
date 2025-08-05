# apps/products/signals.py

import logging
from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Importa tus prefijos de cache y modelos
from apps.products.utils.cache_helpers_products import PRODUCT_LIST_CACHE_PREFIX
from apps.products.utils.cache_helpers_categories import CACHE_KEY_CATEGORY_LIST
from apps.products.utils.cache_helpers_types import CACHE_KEY_TYPE_LIST
from apps.products.utils.cache_helpers_subproducts import SUBPRODUCT_LIST_CACHE_PREFIX

from apps.products.models import Product, Category, Type, Subproduct  # ajusta nombres según tus modelos

logger = logging.getLogger(__name__)

def _clear_pattern(prefix: str):
    pattern = f"*:{prefix}*"
    deleted = 0
    try:
        # primero intenta con el método del cache backend
        deleted = cache.delete_pattern(pattern)
    except Exception:
        # si falla (AttributeError, NotImplementedError, etc), caemos al helper Redis
        try:
            from apps.products.utils.redis_utils import delete_keys_by_pattern
            deleted = delete_keys_by_pattern(pattern)
        except Exception as e:
            logger.error(f"[Cache] Failed to clear keys for pattern {pattern}: {e}")
            return
    finally:
        if not settings.DEBUG:
            logger.debug(f"[Cache] Deleted {deleted} keys matching {pattern}")

# Señal para Product
@receiver([post_save, post_delete], sender=Product)
def clear_product_cache(sender, **kwargs):
    _clear_pattern(PRODUCT_LIST_CACHE_PREFIX)

# Señal para Category
@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, **kwargs):
    _clear_pattern(CACHE_KEY_CATEGORY_LIST)

# Señal para Type
@receiver([post_save, post_delete], sender=Type)
def clear_type_cache(sender, **kwargs):
    _clear_pattern(CACHE_KEY_TYPE_LIST)

# Señal para Subproduct
@receiver([post_save, post_delete], sender=Subproduct)
def clear_subproduct_cache(sender, **kwargs):
    _clear_pattern(SUBPRODUCT_LIST_CACHE_PREFIX)
