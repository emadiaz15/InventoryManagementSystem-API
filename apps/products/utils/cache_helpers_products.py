# apps/products/utils/cache_helpers_products.py

from urllib.parse import urlencode

PRODUCT_LIST_CACHE_PREFIX   = "product_list"
PRODUCT_DETAIL_CACHE_PREFIX = "product_detail"


def product_list_cache_key(page: int = 1, page_size: int = 10, **filters) -> str:
    """
    Genera la clave de cache para GET /api/v1/inventory/products/?...
    Incluye paginación y filtros arbitrarios.
    """
    # Construimos los parámetros y los ordenamos para asegurar consistencia
    params = {"page": page, "page_size": page_size, **filters}
    sorted_items = sorted(params.items())
    query = urlencode(sorted_items)
    # Clave: prefijo + query string (sin host ni esquema)
    return f"{PRODUCT_LIST_CACHE_PREFIX}:{query}"


def product_detail_cache_key(prod_pk: int) -> str:
    """
    Genera la clave de cache para GET /api/v1/inventory/products/<prod_pk>/
    """
    # Clave sencilla basada únicamente en el ID de producto
    return f"{PRODUCT_DETAIL_CACHE_PREFIX}:{prod_pk}"
