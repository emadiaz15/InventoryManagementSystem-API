# apps/products/utils/cache_helpers_subproducts.py

from typing import Any, Dict, Optional
from .cache_helpers_core import generate_cache_key, generate_detail_key

SUBPRODUCT_LIST_CACHE_PREFIX = "subproduct_list"
SUBPRODUCT_DETAIL_CACHE_PREFIX = "subproduct_detail"

def subproduct_list_cache_key(
    prod_pk: int,
    page: int = 1,
    page_size: int = 10,
    status: bool = True,
    **extra_filters: Any
) -> str:
    """
    Clave para listar subproductos de un producto padre,
    incluye IDs, paginación, estado y filtros adicionales.
    """
    params: Dict[str, Any] = {"prod_pk": prod_pk, "page": page, "page_size": page_size, "status": status}
    params.update(extra_filters)
    return generate_cache_key(SUBPRODUCT_LIST_CACHE_PREFIX, **params)


def subproduct_detail_cache_key(
    prod_pk: int,
    subp_pk: int
) -> str:
    """
    Clave para detalle de subproducto específico.
    """
    return generate_detail_key(SUBPRODUCT_DETAIL_CACHE_PREFIX, prod_pk, subp_pk)
