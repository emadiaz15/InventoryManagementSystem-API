# apps/products/utils/cache_helpers_types.py

from urllib.parse import urlencode

CACHE_KEY_TYPE_LIST = "type_list"


def type_list_cache_key(page: int = 1, page_size: int = 10, name: str = "") -> str:
    """
    Genera la clave de cache para GET /inventory/types/?page=&page_size=&name=
    """
    params = {"page": page, "page_size": page_size}
    if name:
        params["name"] = name
    # Ordenar los parámetros para consistencia
    query = urlencode(sorted(params.items()))
    # Key sencilla basada en prefijo y query string
    return f"{CACHE_KEY_TYPE_LIST}:{query}"
