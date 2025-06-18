import os
from mimetypes import guess_type
from storages.backends.s3boto3 import S3Boto3Storage
from apps.storages_client.services.s3_file_access import generate_presigned_url

storage = S3Boto3Storage()

def _validate_file_extension(filename: str):
    allowed = os.getenv("ALLOWED_UPLOAD_EXTENSIONS", ".jpg,.jpeg,.png,.webp,.pdf").split(",")
    _, ext = os.path.splitext(filename.lower())
    if ext not in allowed:
        raise ValueError(f"Extensión de archivo no permitida: {ext}. Permitidas: {allowed}")


def upload_subproduct_file(file, subproduct_id: int) -> dict:
    """
    Sube un archivo al bucket MinIO/S3 en una carpeta por subproducto.
    Solo se aceptan imágenes y PDFs.
    """
    _validate_file_extension(file.name)

    key = f"subproducts/{subproduct_id}/{file.name}"
    storage.save(key, file)

    mime_type, _ = guess_type(file.name)
    url = generate_presigned_url(bucket=storage.bucket_name, object_name=key)

    return {
        "key": key,
        "url": url,
        "name": file.name,
        "mimeType": mime_type or "application/octet-stream"
    }


def delete_subproduct_file(key: str) -> bool:
    """
    Elimina un archivo del bucket MinIO/S3 por su key.
    """
    try:
        storage.delete(key)
        return True
    except Exception as e:
        print(f"❌ Error al eliminar archivo de subproducto ({key}): {e}")
        return False


def get_subproduct_file_url(key: str, expiry_seconds: int = 300) -> str | None:
    """
    Genera una URL presignada temporal para descargar un archivo de subproducto.
    """
    try:
        return generate_presigned_url(bucket=storage.bucket_name, object_name=key, expiry_seconds=expiry_seconds)
    except Exception as e:
        print(f"❌ Error al generar URL presignada para subproducto ({key}): {e}")
        return None
