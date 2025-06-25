from django.conf import settings
from apps.storages_client.clients.minio_client import get_minio_client
import logging
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)

def generate_presigned_url(bucket: str, object_name: str, expiry_seconds: int = 300) -> str:
    """
    Genera una URL presignada temporal para acceder a un objeto privado en MinIO/S3.
    Reemplaza el host interno por el público configurado.
    """
    if not bucket or not object_name:
        raise ValueError("Se requieren bucket y object_name para generar la URL presignada.")

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

        # Reemplaza el host interno (minio) por uno público definido en settings
        parsed_url = urlparse(url)
        public_netloc = settings.MINIO_PUBLIC_URL
        if not public_netloc:
            raise Exception("MINIO_PUBLIC_URL no configurado correctamente.")# Debe ser solo host:puerto, ejemplo 'localhost:9000'

        # Si MINIO_PUBLIC_ENDPOINT es solo dominio, extraelo correctamente
        if "://" in public_netloc:
            public_netloc = urlparse(public_netloc).netloc

        updated_url = urlunparse(parsed_url._replace(netloc=public_netloc))
        return updated_url

    except Exception as e:
        logger.error(f"❌ Error al generar URL presignada para '{object_name}': {str(e)}")
        raise Exception(f"Error al generar URL presignada para '{object_name}': {str(e)}")
