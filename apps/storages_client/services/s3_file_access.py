from django.conf import settings
from apps.storages_client.clients.minio_client import get_minio_client
import logging
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)

def generate_presigned_url(bucket: str, object_name: str, expiry_seconds: int = 300) -> str:
    """
    Genera una URL presignada temporal para acceder a un objeto privado en MinIO/S3.
    Reemplaza host y esquema por los configurados en MINIO_PUBLIC_URL.
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

        # 2) Parseamos la URL y sustituimos host+puerto público y esquema
        parsed = urlparse(url)
        public = settings.MINIO_PUBLIC_URL
        if not public:
            raise Exception("MINIO_PUBLIC_URL no configurado correctamente.")

        pub_parsed = urlparse(public)
        # si public no trae esquema, asumimos http
        scheme = pub_parsed.scheme or 'http'
        netloc = pub_parsed.netloc or pub_parsed.path

        # 3) Reemplazamos scheme y netloc
        secured = parsed._replace(scheme=scheme, netloc=netloc)

        # 4) Reconstruimos la URL final
        return urlunparse(secured)

    except Exception as e:
        logger.error(f"❌ Error al generar URL presignada para '{object_name}': {e}")
        raise Exception(f"Error al generar URL presignada para '{object_name}': {e}")
