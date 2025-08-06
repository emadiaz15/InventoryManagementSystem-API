# apps/products/utils/redis_utils.py

import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

def delete_keys_by_pattern(prefix: str) -> int:
    """
    Invalida todas las claves cuyo prefijo coincida con prefix,
    respetando el KEY_PREFIX configurado en settings.CACHES.
    """
    # Obtener el prefijo global de cache (si existe)
    key_prefix = settings.CACHES['default'].get('KEY_PREFIX', '')

    # Construir el patrón completo para delete_pattern
    if key_prefix:
        pattern = f"{key_prefix}:{prefix}:*"
    else:
        pattern = f"{prefix}:*"

    try:
        deleted = cache.delete_pattern(pattern)
        logger.debug("[Cache] borradas %d claves con patrón '%s'", deleted, pattern)
        return deleted
    except (AttributeError, NotImplementedError) as e:
        logger.warning(
            "[Cache] backend no soporta delete_pattern; no se borraron claves para '%s' (%s)",
            pattern, e
        )
        return 0
