# apps/products/signals.py

import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.products.models import Product, Category, Type, Subproduct
from apps.products.utils.redis_utils import delete_keys_by_pattern
from apps.products.utils.cache_helpers_categories import CACHE_KEY_CATEGORY_LIST
from apps.products.utils.cache_helpers_types      import CACHE_KEY_TYPE_LIST
from apps.products.utils.cache_helpers_products   import (
    PRODUCT_LIST_CACHE_PREFIX,
    PRODUCT_DETAIL_CACHE_PREFIX,
)
from apps.products.utils.cache_helpers_subproducts import (
    SUBPRODUCT_LIST_CACHE_PREFIX,
    SUBPRODUCT_DETAIL_CACHE_PREFIX,
)

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, **kwargs):
    """
    Invalida la caché de la lista de categorías tras crear, actualizar o borrar.
    """
    deleted = delete_keys_by_pattern(CACHE_KEY_CATEGORY_LIST)
    logger.debug("[Cache][Signal] category_list borrado (%d claves).", deleted)


@receiver([post_save, post_delete], sender=Type)
def clear_type_cache(sender, **kwargs):
    """
    Invalida la caché de la lista de tipos tras crear, actualizar o borrar.
    """
    deleted = delete_keys_by_pattern(CACHE_KEY_TYPE_LIST)
    logger.debug("[Cache][Signal] type_list borrado (%d claves).", deleted)


@receiver([post_save, post_delete], sender=Product)
def clear_product_cache(sender, **kwargs):
    """
    Invalida la caché de lista y detalle de productos tras crear, actualizar o borrar.
    """
    deleted_list   = delete_keys_by_pattern(PRODUCT_LIST_CACHE_PREFIX)
    deleted_detail = delete_keys_by_pattern(PRODUCT_DETAIL_CACHE_PREFIX)
    logger.debug(
        "[Cache][Signal] product_list borrado (%d), product_detail borrado (%d).",
        deleted_list, deleted_detail
    )


@receiver([post_save, post_delete], sender=Subproduct)
def clear_subproduct_cache(sender, **kwargs):
    """
    Invalida la caché de lista y detalle de subproductos tras crear, actualizar o borrar.
    """
    deleted_list   = delete_keys_by_pattern(SUBPRODUCT_LIST_CACHE_PREFIX)
    deleted_detail = delete_keys_by_pattern(SUBPRODUCT_DETAIL_CACHE_PREFIX)
    logger.debug(
        "[Cache][Signal] subproduct_list borrado (%d), subproduct_detail borrado (%d).",
        deleted_list, deleted_detail
    )
