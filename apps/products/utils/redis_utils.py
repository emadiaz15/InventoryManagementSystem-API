import os
import redis
from django_redis import get_redis_connection
from typing import Any, List, Optional

def get_redis_client(use_django: bool = True) -> redis.Redis:
    """
    Devuelve una instancia de cliente Redis.
    - Si use_django=True, intenta usar django-redis ("default").
      Si ese backend falla (por configuración o porque no soporta SCAN), 
      hace fallback a conexión directa usando REDIS_URL.
    - En caso contrario, crea un cliente redis.Redis a partir de REDIS_URL.
    """
    if use_django:
        try:
            return get_redis_connection("default")
        except Exception:
            # Cae al cliente directo si django-redis no sirve
            url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            return redis.from_url(url, decode_responses=True)

    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(url, decode_responses=True)


def delete_keys_by_pattern(
    pattern: str,
    use_django: bool = True,
    batch_size: int = 500
) -> int:
    """
    Elimina todas las claves que coincidan con un patrón usando SCAN + pipeline.
    Si el cliente django-redis no soporta SCAN, hace fallback a conexión directa.
    Retorna el número total de claves borradas.
    """
    def _scan_delete(client):
        cursor = 0
        total_deleted = 0
        while True:
            cursor, keys = client.scan(cursor=cursor, match=pattern, count=batch_size)
            if keys:
                with client.pipeline() as pipe:
                    for key in keys:
                        pipe.delete(key)
                    deleted = pipe.execute()
                total_deleted += sum(deleted)
            if cursor == 0:
                break
        return total_deleted

    # Intentamos primero con django-redis (o el cliente pasado)
    client = get_redis_client(use_django)
    try:
        return _scan_delete(client)
    except NotImplementedError:
        # Fallback : usamos conexión directa a Redis
        client_direct = get_redis_client(False)
        return _scan_delete(client_direct)


def get_keys_by_pattern(
    pattern: str,
    use_django: bool = True,
    batch_size: int = 500
) -> List[str]:
    """
    Devuelve lista de claves que casan con el patrón.
    """
    client = get_redis_client(use_django)
    cursor = 0
    results: List[str] = []
    while True:
        cursor, batch = client.scan(cursor=cursor, match=pattern, count=batch_size)
        results.extend(batch)
        if cursor == 0:
            break
    return results


def set_value(
    key: str,
    value: Any,
    ex: Optional[int] = None,
    use_django: bool = True
) -> bool:
    """
    Guarda un valor en Redis con expiración opcional.
    """
    client = get_redis_client(use_django)
    return client.set(key, value, ex=ex)


def get_value(
    key: str,
    use_django: bool = True
) -> Optional[str]:
    """
    Recupera el valor de una clave o None.
    """
    client = get_redis_client(use_django)
    return client.get(key)


def delete_key(
    key: str,
    use_django: bool = True
) -> int:
    """
    Elimina una clave específica. Retorna 1 si se borró.
    """
    client = get_redis_client(use_django)
    return client.delete(key)
