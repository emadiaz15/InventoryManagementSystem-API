# apps/products/utils/cache_helpers_products.py

# Solo definimos los prefijos lógicos; las funciones de generación
# de key manual (generate_cache_key, generate_detail_key) quedan
# disponibles para otros usos si los necesitas.

PRODUCT_LIST_CACHE_PREFIX    = "product_list"
PRODUCT_DETAIL_CACHE_PREFIX  = "product_detail"

def product_list_cache_key(page: int = 1, page_size: int = 10, **filters) -> str:
    """
    (Opcional) Genera una clave manual de listing si la necesitas en otro contexto.
    """
    from .cache_helpers_core import generate_cache_key
    return generate_cache_key(PRODUCT_LIST_CACHE_PREFIX, page=page, page_size=page_size, **filters)

def product_detail_cache_key(prod_pk: int) -> str:
    """
    (Opcional) Genera una clave manual de detalle si la necesitas en otro contexto.
    """
    from .cache_helpers_core import generate_detail_key
    return generate_detail_key(PRODUCT_DETAIL_CACHE_PREFIX, prod_pk)
