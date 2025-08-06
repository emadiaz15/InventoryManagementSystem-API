# apps/products/utils/redis_utils.py

import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

def delete_keys_by_pattern(prefix: str) -> int:
    """
    Invalida todas las claves cuyo prefijo coincida con prefix,
    respetando el KEY_PREFIX configurado en settings.CACHES
    y capturando también los sufijos automáticos de cache_page.
    """
    # Obtener el prefijo global de cache (si existe)
    key_prefix = settings.CACHES['default'].get('KEY_PREFIX', '')

    # Construir un patrón amplio que incluya versión y view prefix
    # e.g. "inventory_prod:*product_list*"
    if key_prefix:
        pattern = f"{key_prefix}:*{prefix}*"
    else:
        pattern = f"*{prefix}*"

    # 1) Intentamos con delete_pattern (django-redis)
    try:
        deleted = cache.delete_pattern(pattern)
        logger.debug("[Cache] borradas %d claves con patrón '%s'", deleted, pattern)
        return deleted
    except (AttributeError, NotImplementedError) as e:
        logger.warning(
            "[Cache] backend no soporta delete_pattern; patrón '%s' no procesado (%s)",
            pattern, e
        )

    # 2) Fallback para LocMemCache (cache._cache es un dict)
    if hasattr(cache, "_cache") and isinstance(cache._cache, dict):
        # aquí buscamos solo el sufijo lógico en la clave
        to_delete = [key for key in cache._cache if prefix in key]
        for key in to_delete:
            cache.delete(key)
        deleted = len(to_delete)
        logger.debug(
            "[Cache][LocMemCache] borradas %d claves que contienen '%s'", deleted, prefix
        )
        return deleted

    # 3) Otros backends sin soporte
    logger.warning(
        "[Cache] backend sin soporte para delete_pattern ni LocMemCache; "
        "no se invalidó el patrón '%s'", pattern
    )
    return 0
