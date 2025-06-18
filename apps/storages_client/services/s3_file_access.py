from datetime import timedelta, datetime
from urllib.parse import quote_plus

from django.conf import settings
from apps.storages_client.clients.minio_client import get_minio_client


def generate_presigned_url(bucket: str, object_name: str, expiry_seconds: int = 300) -> str:
    """
    Genera una URL presignada temporal para acceder a un objeto privado en MinIO/S3.

    Args:
        bucket (str): Nombre del bucket.
        object_name (str): Clave/ID del archivo en S3.
        expiry_seconds (int): Tiempo de expiración en segundos (default: 5 minutos).

    Returns:
        str: URL firmada para acceso temporal.
    """
    client = get_minio_client()

    try:
        url = client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket,
                'Key': object_name,
            },
            ExpiresIn=expiry_seconds
        )
        return url
    except Exception as e:
        raise Exception(f"Error al generar URL presignada para '{object_name}': {str(e)}")
