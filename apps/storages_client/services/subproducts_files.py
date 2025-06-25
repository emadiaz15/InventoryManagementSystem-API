import os
import uuid
from mimetypes import guess_type
from django.conf import settings
from apps.storages_client.clients.minio_client import get_minio_client
from apps.storages_client.services.s3_file_access import generate_presigned_url


def _validate_file_extension(filename: str):
    """
    Valida que la extensión del archivo sea permitida.
    """
    allowed = os.getenv("ALLOWED_UPLOAD_EXTENSIONS", ".jpg,.jpeg,.png,.webp,.pdf,.mp4,.mov,.avi").split(",")
    _, ext = os.path.splitext(filename.lower())
    if ext not in allowed:
        raise ValueError(f"Extensión de archivo no permitida: {ext}. Permitidas: {allowed}")


def upload_subproduct_file(file, product_id: int, subproduct_id: int) -> dict:
    """
    Sube un archivo al bucket de productos, organizándolo dentro del producto y subproducto.
    """
    _validate_file_extension(file.name)

    _, ext = os.path.splitext(file.name)
    unique_id = uuid.uuid4().hex
    key = f"products/{product_id}/subproducts/{subproduct_id}/{unique_id}{ext}"

    s3 = get_minio_client()
    file.seek(0)

    s3.upload_fileobj(
        Fileobj=file,
        Bucket=settings.AWS_PRODUCT_BUCKET_NAME,
        Key=key,
        ExtraArgs={"ContentType": file.content_type},
    )

    mime_type, _ = guess_type(file.name)
    url = generate_presigned_url(bucket=settings.AWS_PRODUCT_BUCKET_NAME, object_name=key)

    return {
        "key": key,
        "url": url,
        "name": file.name,
        "mimeType": mime_type or "application/octet-stream"
    }


def delete_subproduct_file(key: str) -> bool:
    """
    Elimina un archivo de subproducto por su key.
    """
    s3 = get_minio_client()

    try:
        s3.delete_object(Bucket=settings.AWS_PRODUCT_BUCKET_NAME, Key=key)
        return True
    except Exception as e:
        print(f"❌ Error al eliminar archivo de subproducto ({key}): {e}")
        return False


def get_subproduct_file_url(key: str, expiry_seconds: int = 300) -> str | None:
    """
    Genera una URL presignada temporal para acceder al archivo de subproducto.
    """
    try:
        return generate_presigned_url(
            bucket=settings.AWS_PRODUCT_BUCKET_NAME,
            object_name=key,
            expiry_seconds=expiry_seconds
        )
    except Exception as e:
        print(f"❌ Error al generar URL presignada para subproducto ({key}): {e}")
        return None
