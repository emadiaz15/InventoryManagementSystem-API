import os
import redis
from django_redis import get_redis_connection
from typing import Union, Optional, List

def get_redis_client(use_django: bool = True) -> redis.Redis:
    """
    Devuelve una instancia de cliente Redis.
    - Si use_django=True, usa la configuración de django-redis ("default" en settings).
    - En caso contrario, crea un cliente redis.Redis a partir de la URL en REDIS_URL.
    """
    if use_django:
        return get_redis_connection("default")
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(url, decode_responses=True)


def delete_keys_by_pattern(
    pattern: str,
    use_django: bool = True,
    batch_size: int = 1000
) -> int:
    """
    Elimina todas las claves que coincidan con el patrón dado.
    - pattern: patrón compatible con SCAN, e.g. "prefix:*"
    - batch_size: tamaño de lote para pipeline.
    Devuelve el número total de claves eliminadas.
    """
    r = get_redis_client(use_django)
    cursor = 0
    total_deleted = 0

    try:
        while True:
            cursor, keys = r.scan(cursor=cursor, match=pattern, count=batch_size)
            if keys:
                # borrado en bloque para eficiencia
                with r.pipeline() as pipe:
                    for k in keys:
                        pipe.delete(k)
                    deleted_counts = pipe.execute()
                total_deleted += sum(deleted_counts)
            if cursor == 0:
                break
    except Exception as e:
        # evita que un fallo interrumpa el proceso completo
        print(f"Error borrando claves Redis con patrón {pattern}: {e}")
    return total_deleted


def get_keys_by_pattern(
    pattern: str,
    use_django: bool = True,
    batch_size: int = 1000
) -> List[str]:
    """
    Devuelve la lista de claves que coinciden con el patrón.
    """
    r = get_redis_client(use_django)
    cursor = 0
    keys: List[str] = []
    while True:
        cursor, batch = r.scan(cursor=cursor, match=pattern, count=batch_size)
        keys.extend(batch)
        if cursor == 0:
            break
    return keys


def set_value(
    key: str,
    value: Union[str, bytes, int, float],
    ex: Optional[int] = None,
    use_django: bool = True
) -> bool:
    """
    Guarda un valor en Redis.
    - key: clave
    - value: puede ser str, bytes, número
    - ex: tiempo de expiración en segundos (opcional)
    """
    r = get_redis_client(use_django)
    return r.set(key, value, ex=ex)


def get_value(key: str, use_django: bool = True) -> Optional[str]:
    """
    Recupera un valor de Redis. Devuelve None si no existe.
    """
    r = get_redis_client(use_django)
    return r.get(key)


def delete_key(key: str, use_django: bool = True) -> int:
    """
    Elimina una clave concreta de Redis.
    Devuelve el número de claves eliminadas (0 o 1).
    """
    r = get_redis_client(use_django)
    return r.delete(key)
