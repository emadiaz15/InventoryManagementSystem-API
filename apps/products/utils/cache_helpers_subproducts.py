# apps/products/utils/cache_helpers_subproducts.py

from urllib.parse import urlencode

# Prefijos de caché (key_prefix en @cache_page)
SUBPRODUCT_LIST_CACHE_PREFIX = "subproduct_list"
SUBPRODUCT_DETAIL_CACHE_PREFIX = "subproduct_detail"


def subproduct_list_cache_key(
    prod_pk: int,
    page: int = 1,
    page_size: int = 10,
    status: bool = True,
    extra_filters: dict | None = None
) -> str:
    """
    Genera la clave de caché que usa @cache_page para:
      GET /api/v1/inventory/products/{prod_pk}/subproducts/?...
    Incluye página, tamaño, status y cualquier filtro adicional.
    """
    # Construimos parámetros y los ordenamos para consistencia
    params = {
        "prod_pk": prod_pk,
        "page": page,
        "page_size": page_size,
        "status": str(status).lower(),
    }
    if extra_filters:
        params.update(extra_filters)

    sorted_items = sorted(params.items())
    query_string = urlencode(sorted_items)
    # Key sencilla: prefix + parámetros serializados
    return f"{SUBPRODUCT_LIST_CACHE_PREFIX}:{query_string}"


def subproduct_detail_cache_key(
    prod_pk: int,
    subp_pk: int
) -> str:
    """
    Genera la clave de caché para el detalle de un subproducto:
      GET /api/v1/inventory/products/{prod_pk}/subproducts/{subp_pk}/
    """
    # Clave basada en IDs de producto y subproducto
    return f"{SUBPRODUCT_DETAIL_CACHE_PREFIX}:{prod_pk}:{subp_pk}"
