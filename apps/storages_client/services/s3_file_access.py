from django.conf import settings
from apps.storages_client.clients.minio_client import get_minio_client
import logging
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)

def generate_presigned_url(bucket: str, object_name: str, expiry_seconds: int = 300) -> str:
    """
    Genera una URL presignada temporal para acceder a un objeto privado en MinIO/S3.
    Reemplaza el host interno por el público configurado y fuerza HTTPS.
    """
    if not bucket or not object_name:
        raise ValueError("Se requieren bucket y object_name para generar la URL presignada.")

    client = get_minio_client()

    try:
        # 1) Generamos la URL presignada con MinIO
        url = client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket, 'Key': object_name},
            ExpiresIn=expiry_seconds
        )

        # 2) Parseamos la URL y sustituimos host+puerto público
        parsed = urlparse(url)
        public = settings.MINIO_PUBLIC_URL
        if not public:
            raise Exception("MINIO_PUBLIC_URL no configurado correctamente.")
        # Extraemos solo netloc si viene con esquema
        public_netloc = urlparse(public).netloc or public

        # 3) Reemplazamos scheme y netloc
        secured = parsed._replace(scheme="https", netloc=public_netloc)

        # 4) Reconstruimos la URL final
        final_url = urlunparse(secured)
        return final_url

    except Exception as e:
        logger.error(f"❌ Error al generar URL presignada para '{object_name}': {e}")
        raise Exception(f"Error al generar URL presignada para '{object_name}': {e}")
