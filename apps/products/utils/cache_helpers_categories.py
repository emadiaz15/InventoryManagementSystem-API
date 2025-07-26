# apps/products/utils/cache_helpers_categories.py

from django.test.client import RequestFactory
from django.utils.cache import _generate_cache_key

# La clave que usa @cache_page
CACHE_KEY_CATEGORY_LIST = "category_list"


def category_list_cache_key(page: int = 1, page_size: int = 10, name: str = "") -> str:
    """
    Genera la misma clave que @cache_page(…, key_prefix=CACHE_KEY_CATEGORY_LIST)
    para /api/v1/inventory/categories/?page=…&page_size=…&name=…
    """
    # Ajusta la URL base si tu prefix/API es distinta
    url = f"/api/v1/inventory/categories/?page={page}&page_size={page_size}"
    if name:
        url += f"&name={name}"
    fake_req = RequestFactory().get(url)
    return _generate_cache_key(fake_req, "GET", [], CACHE_KEY_CATEGORY_LIST)
