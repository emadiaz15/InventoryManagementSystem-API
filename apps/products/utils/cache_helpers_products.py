# apps/products/utils/cache_helpers_products.py

from typing import Any, Dict
from .cache_helpers_core import generate_cache_key, generate_detail_key

PRODUCT_LIST_CACHE_PREFIX = "product_list"
PRODUCT_DETAIL_CACHE_PREFIX = "product_detail"

def product_list_cache_key(
    page: int = 1,
    page_size: int = 10,
    **filters: Any
) -> str:
    """
    Clave para listar productos con paginación y filtros arbitrarios.
    """
    return generate_cache_key(PRODUCT_LIST_CACHE_PREFIX, page=page, page_size=page_size, **filters)


def product_detail_cache_key(prod_pk: int) -> str:
    """
    Clave para detalle de un producto.
    """
    return generate_detail_key(PRODUCT_DETAIL_CACHE_PREFIX, prod_pk)
