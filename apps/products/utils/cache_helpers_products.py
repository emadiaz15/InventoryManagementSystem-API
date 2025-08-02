# apps/products/utils/cache_helpers_products.py

from django.test.client import RequestFactory
from django.utils.cache import _generate_cache_key
from urllib.parse import urlencode

PRODUCT_LIST_CACHE_PREFIX    = "product_list"
PRODUCT_DETAIL_CACHE_PREFIX  = "product_detail"

def product_list_cache_key(page: int = 1, page_size: int = 10, **filters) -> str:
    """
    Genera la clave de cache para GET /api/v1/inventory/products/?...
    Incluye paginación y filtros arbitrarios.
    """
    params = {"page": page, "page_size": page_size, **filters}
    query = urlencode(params)
    rf = RequestFactory()
    fake_req = rf.get(f"/api/v1/inventory/products/?{query}")
    return _generate_cache_key(fake_req, "GET", [], PRODUCT_LIST_CACHE_PREFIX)

def product_detail_cache_key(prod_pk: int) -> str:
    """
    Genera la clave de cache para GET /api/v1/inventory/products/<prod_pk>/
    """
    rf = RequestFactory()
    fake_req = rf.get(f"/api/v1/inventory/products/{prod_pk}/")
    return _generate_cache_key(fake_req, "GET", [], PRODUCT_DETAIL_CACHE_PREFIX)
