# apps/products/utils/cache_helpers_core.py

"""
Módulo central para generación de claves de caché y utilidades comunes.
"""
from urllib.parse import urlencode
from typing import Any, Dict, List, Tuple


def generate_cache_key(prefix: str, **params: Any) -> str:
    """
    Genera una clave de caché a partir de un prefijo y parámetros arbitrarios.
    - prefix: texto antes de ':'
    - params: pares clave=valor que serán serializados ordenadamente
    Ejemplo: generate_cache_key('product_list', page=1, size=10)
    -> 'product_list:page=1&size=10'
    """
    # Convertir todos los valores a str y ordenar
    items: List[Tuple[str, str]] = sorted((k, str(v)) for k, v in params.items())
    query_string = urlencode(items)
    return f"{prefix}:{query_string}"


def generate_detail_key(prefix: str, *ids: Any) -> str:
    """
    Genera una clave de caché para endpoints de detalle, concatenando IDs.
    Ejemplo: generate_detail_key('product_detail', prod_id)
             -> 'product_detail:42'
    Ejemplo múltiple: generate_detail_key('subproduct_detail', prod_id, subp_id)
             -> 'subproduct_detail:42:7'
    """
    id_parts = ":".join(str(i) for i in ids)
    return f"{prefix}:{id_parts}"
