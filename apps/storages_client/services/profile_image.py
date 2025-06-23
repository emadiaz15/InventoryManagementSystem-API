import os
import logging
from uuid import uuid4
from django.conf import settings
from apps.storages_client.clients.minio_client import get_minio_client
from apps.storages_client.services.s3_file_access import generate_presigned_url

logger = logging.getLogger(__name__)

__all__ = [
    "upload_profile_image",
    "replace_profile_image",
    "delete_profile_image",
    "get_profile_image_url"
]


def _validate_file_extension(filename: str):
    """
    Solo se permiten archivos de imagen.
    """
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    _, ext = os.path.splitext(filename.lower())

    if ext not in allowed_extensions:
        raise ValueError(f"Extensión no permitida: {ext}. Solo se permiten imágenes: {allowed_extensions}")


def upload_profile_image(file, user_id: int) -> dict:
    """
    Sube una nueva imagen de perfil al bucket correspondiente.
    """
    _validate_file_extension(file.name)

    _, ext = os.path.splitext(file.name)
    filename = f"profile-images/{user_id}_{uuid4().hex}{ext}"

    s3 = get_minio_client()
    file.seek(0)

    logger.info(f"⬆️ Subiendo imagen de perfil para user_id={user_id} a {filename}")

    try:
        s3.upload_fileobj(
            Fileobj=file,
            Bucket=settings.AWS_PROFILE_BUCKET_NAME,
            Key=filename,
            ExtraArgs={"ContentType": file.content_type},
        )
    except Exception as e:
        logger.error(f"❌ Error al subir imagen de perfil: {e}")
        raise Exception("Error al subir la imagen de perfil.")

    url = generate_presigned_url(bucket=settings.AWS_PROFILE_BUCKET_NAME, object_name=filename)
    return {"url": url, "key": filename}


def replace_profile_image(file, file_id: str, user_id: int) -> dict:
    """
    Reemplaza la imagen de perfil existente.
    """
    _validate_file_extension(file.name)

    logger.info(f"♻️ Reemplazando imagen de perfil {file_id} para user_id={user_id}")

    s3 = get_minio_client()
    file.seek(0)

    try:
        s3.upload_fileobj(
            Fileobj=file,
            Bucket=settings.AWS_PROFILE_BUCKET_NAME,
            Key=file_id,
            ExtraArgs={"ContentType": file.content_type},
        )
    except Exception as e:
        logger.error(f"❌ Error al reemplazar imagen de perfil: {e}")
        raise Exception("Error al reemplazar la imagen de perfil.")

    url = generate_presigned_url(bucket=settings.AWS_PROFILE_BUCKET_NAME, object_name=file_id)
    return {"url": url, "key": file_id}


def delete_profile_image(file_id: str, user_id: int) -> dict:
    """
    Elimina la imagen de perfil.
    """
    logger.info(f"🗑️ Eliminando imagen de perfil {file_id} para user_id={user_id}")

    s3 = get_minio_client()

    try:
        s3.delete_object(Bucket=settings.AWS_PROFILE_BUCKET_NAME, Key=file_id)
    except Exception as e:
        logger.error(f"❌ Error al eliminar imagen de perfil: {e}")
        raise Exception("Error al eliminar la imagen de perfil.")

    return {"message": "Deleted", "key": file_id}


def get_profile_image_url(file_id: str, expiry_seconds: int = 300) -> str:
    """
    Genera una URL presignada temporal para visualizar la imagen de perfil.
    """
    logger.debug(f"🔐 Generando URL firmada para {file_id}")

    return generate_presigned_url(
        bucket=settings.AWS_PROFILE_BUCKET_NAME,
        object_name=file_id,
        expiry_seconds=expiry_seconds
    )
