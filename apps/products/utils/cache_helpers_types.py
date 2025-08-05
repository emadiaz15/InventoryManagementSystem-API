# apps/products/utils/cache_helpers_types.py

from typing import Optional
from .cache_helpers_core import generate_cache_key

CACHE_KEY_TYPE_LIST = "type_list"

def type_list_cache_key(
    page: int = 1,
    page_size: int = 10,
    name: Optional[str] = None
) -> str:
    """
    Clave para listar tipos con paginación y filtro opcional por nombre.
    """
    params = {"page": page, "page_size": page_size}
    if name:
        params["name"] = name
    return generate_cache_key(CACHE_KEY_TYPE_LIST, **params)