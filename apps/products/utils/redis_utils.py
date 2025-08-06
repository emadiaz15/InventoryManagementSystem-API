# apps/products/utils/redis_utils.py

import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

def delete_keys_by_pattern(prefix: str) -> int:
    """
    Invalida todas las claves cuyo prefijo coincida con prefix.
    - Con RedisCache usa delete_pattern.
    - Con LocMemCache recorre cache._cache y borra manualmente.
    """
    pattern = f"{prefix}:"
    deleted = 0

    # 1) Intentamos con delete_pattern (django-redis)
    try:
        deleted = cache.delete_pattern(pattern + "*")
        return deleted
    except (AttributeError, NotImplementedError):
        pass

    # 2) Si el backend expone _cache (LocMemCache)
    #    cache._cache es un dict {clave: (valor, expire_time)}
    if hasattr(cache, "_cache") and isinstance(cache._cache, dict):
        to_delete = [key for key in cache._cache if key.startswith(pattern)]
        for key in to_delete:
            cache.delete(key)
        deleted = len(to_delete)
        logger.debug(
            "[Cache][LocMemCache] borradas %d claves cuyo prefijo es '%s'",
            deleted, prefix
        )
        return deleted

    # 3) Otros backends sin soporte
    logger.warning(
        "El backend de cache no soporta delete_pattern ni _cache; "
        "se omite la invalidación del patrón '%s*'.", pattern
    )
    return 0
