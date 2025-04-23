import os
import requests
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# -------------------------------------------------------------------
# Configuración: sacamos la URL y la clave compartida de Django settings
# -------------------------------------------------------------------
DRIVE_API_BASE_URL = getattr(settings, "DRIVE_API_BASE_URL", None)
DRIVE_SHARED_SECRET = getattr(settings, "DRIVE_SHARED_SECRET", None)
if not DRIVE_API_BASE_URL or not DRIVE_SHARED_SECRET:
    raise ImproperlyConfigured(
        "Faltan variables de entorno para la API de almacenamiento: "
        "DRIVE_API_BASE_URL y/o DRIVE_SHARED_SECRET"
    )

# Tiempo de vida del JWT que enviamos al servicio FastAPI
JWT_TTL = timedelta(minutes=10)


def generate_jwt(user_id: int) -> str:
    """
    Genera un JWT con el claim 'user_id' para que el servicio FastAPI pueda
    diferenciar usuarios si lo necesita.
    """
    payload = {
        "sub": "django-backend",
        "user_id": user_id,
        "exp": datetime.utcnow() + JWT_TTL,
    }
    return jwt.encode(payload, DRIVE_SHARED_SECRET, algorithm="HS256")


def upload_profile_image(file, user_id: int) -> dict:
    """
    Sube una imagen de perfil al endpoint /profile/ de FastAPI.
    - file: instancia de Django UploadedFile
    - user_id: ID numérico del usuario que sube la foto
    Devuelve el JSON de respuesta, e.g. {"message":"...","file_id":"..."}.
    """
    token = generate_jwt(user_id)
    # Aseguramos que no haya doble slash al concatenar
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/profile/"

    # Leemos contenido y sacamos extensión
    data = file.read()
    _, ext = os.path.splitext(file.name)
    filename = f"{user_id}{ext}"

    files = {
        "file": (
            filename,
            data,
            getattr(file, "content_type", "application/octet-stream")
        )
    }
    headers = {"x-api-key": f"Bearer {token}"}

    resp = requests.post(url, headers=headers, files=files)
    resp.raise_for_status()
    return resp.json()

def delete_profile_image(file_id: str, user_id: int):
    """Elimina una imagen del servicio FastAPI."""
    token = generate_jwt(user_id)
    url = f"{DRIVE_API_BASE_URL.rstrip('/')}/profile/delete/{file_id}"
    headers = {"x-api-key": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.json()