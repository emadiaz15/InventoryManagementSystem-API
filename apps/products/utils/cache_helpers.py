from django.test.client import RequestFactory
from django.utils.cache import _generate_cache_key

# Prefijos de caché
PRODUCT_LIST_CACHE_PREFIX = "product_list"
PRODUCT_DETAIL_CACHE_PREFIX = "product_detail"
SUBPRODUCT_LIST_CACHE_PREFIX = "subproduct_list"
SUBPRODUCT_DETAIL_CACHE_PREFIX = "subproduct_detail"


def product_list_cache_key():
    """
    Genera la clave de caché para la lista de productos.
    """
    rf = RequestFactory()
    req = rf.get("/api/v1/inventory/products/")
    return _generate_cache_key(req, "GET", [], PRODUCT_LIST_CACHE_PREFIX)


def product_detail_cache_key(prod_pk):
    """
    Genera la clave de caché para el detalle de un producto.
    """
    rf = RequestFactory()
    req = rf.get(f"/api/v1/inventory/products/{prod_pk}/")
    return _generate_cache_key(req, "GET", [], PRODUCT_DETAIL_CACHE_PREFIX)


def subproduct_list_cache_key(prod_pk):
    """
    Genera la clave de caché para la lista de subproductos de un producto.
    """
    rf = RequestFactory()
    req = rf.get(f"/api/v1/inventory/products/{prod_pk}/subproducts/")
    return _generate_cache_key(req, "GET", [], SUBPRODUCT_LIST_CACHE_PREFIX)


def subproduct_detail_cache_key(prod_pk, subp_pk):
    """
    Genera la clave de caché para el detalle de un subproducto.
    """
    rf = RequestFactory()
    req = rf.get(f"/api/v1/inventory/products/{prod_pk}/subproducts/{subp_pk}/")
    return _generate_cache_key(req, "GET", [], SUBPRODUCT_DETAIL_CACHE_PREFIX)
