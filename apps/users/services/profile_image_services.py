import os
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from apps.drive.utils.jwt_utils import generate_jwt

# -------------------------------------------------------------------
# Configuración: sacamos la URL y la clave compartida de Django settings
# -------------------------------------------------------------------
DRIVE_API_BASE_URL = getattr(settings, "DRIVE_API_BASE_URL", None)
if not DRIVE_API_BASE_URL:
    raise ImproperlyConfigured(
        "Falta la variable DRIVE_API_BASE_URL en la configuración."
    )


def upload_profile_image(file, user_id: int) -> dict:
    """
    Sube una imagen de perfil al endpoint /profile/ de FastAPI.
    - file: instancia de Django UploadedFile
    - user_id: ID numérico del usuario que sube la foto
    Devuelve el JSON de respuesta, e.g. {"message":"...","file_id":"..."}.
    """
    token = generate_jwt({"user_id": user_id})
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/profile/"

    _, ext = os.path.splitext(file.name)
    filename = f"{user_id}{ext}"
    
    file.seek(0)
    file_bytes = file.read()
    
    files = {
        "file": (
            filename,
            file_bytes,
            getattr(file, "content_type", "application/octet-stream")
        )
    }
    headers = {"x-api-key": f"Bearer {token}"}

    resp = requests.post(url, headers=headers, files=files)
    resp.raise_for_status()
    return resp.json()


def replace_profile_image(file, file_id: str, user_id: int) -> dict:
    """
    Reemplaza una imagen de perfil existente en el endpoint /profile/{file_id}.
    """
    token = generate_jwt({"user_id": user_id})
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/profile/{file_id}"

    _, ext = os.path.splitext(file.name)
    filename = f"{user_id}{ext}"

    file.seek(0)
    file_bytes = file.read()

    files = {
        "new_file": (
            filename,
            file_bytes,
            getattr(file, "content_type", "application/octet-stream")
        )
    }
    headers = {"x-api-key": f"Bearer {token}"}

    resp = requests.put(url, headers=headers, files=files)
    resp.raise_for_status()
    return resp.json()


def delete_profile_image(file_id: str, user_id: int):
    """
    Elimina una imagen de perfil del servicio FastAPI.
    """
    token = generate_jwt({"user_id": user_id})
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/profile/delete/{file_id}"
    headers = {"x-api-key": f"Bearer {token}"}

    resp = requests.delete(url, headers=headers)
    resp.raise_for_status()
    return resp.json()
