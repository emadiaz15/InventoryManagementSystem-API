# apps/products/utils/cache_helpers_categories.py

from urllib.parse import urlencode

# Prefijo de cache para @cache_page
CACHE_KEY_CATEGORY_LIST = "category_list"


def category_list_cache_key(page: int = 1, page_size: int = 10, name: str = "") -> str:
    """
    Genera la clave de cache para GET /api/v1/inventory/categories/?page=&page_size=&name=
    """
    # Construye y ordena parámetros para consistencia
    params = {"page": page, "page_size": page_size}
    if name:
        params["name"] = name
    query = urlencode(sorted(params.items()))
    # Key sencilla basada en prefijo y query string
    return f"{CACHE_KEY_CATEGORY_LIST}:{query}"
