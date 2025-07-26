# apps/products/utils/cache_helpers_types.py

from django.test.client import RequestFactory
from django.utils.cache import _generate_cache_key

CACHE_KEY_TYPE_LIST = "type_list"

def type_list_cache_key(page: int = 1, page_size: int = 10, name: str = "") -> str:
    """
    Genera la misma clave que @cache_page usa para /inventory/types/?...
    """
    rf = RequestFactory()
    url = f"/api/v1/inventory/types/?page={page}&page_size={page_size}"
    if name:
        url += f"&name={name}"
    fake_req = rf.get(url)
    return _generate_cache_key(fake_req, "GET", [], CACHE_KEY_TYPE_LIST)
