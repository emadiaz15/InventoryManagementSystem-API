# apps/products/utils/cache_helpers_categories.py

from typing import Optional
from .cache_helpers_core import generate_cache_key

CACHE_KEY_CATEGORY_LIST = "category_list"

def category_list_cache_key(
    page: int = 1,
    page_size: int = 10,
    name: Optional[str] = None
) -> str:
    """
    Clave para listar categorías con paginación y filtro opcional por nombre.
    """
    params = {"page": page, "page_size": page_size}
    if name:
        params["name"] = name
    return generate_cache_key(CACHE_KEY_CATEGORY_LIST, **params)
