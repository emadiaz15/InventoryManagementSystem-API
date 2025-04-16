import os
import requests
import jwt
from datetime import datetime, timedelta
from django.core.exceptions import ImproperlyConfigured

DRIVE_API_BASE_URL = os.getenv("DRIVE_API_BASE_URL")
DRIVE_SHARED_SECRET = os.getenv("DRIVE_SHARED_SECRET")

if not DRIVE_API_BASE_URL or not DRIVE_SHARED_SECRET:
    raise ImproperlyConfigured("Faltan variables de entorno para la API de almacenamiento.")

def generate_jwt():
    payload = {
        "sub": "django-backend",
        "exp": datetime.utcnow() + timedelta(minutes=10),
    }
    return jwt.encode(payload, DRIVE_SHARED_SECRET, algorithm="HS256")

def upload_profile_image(file):
    """
    Sube una imagen de perfil al servicio externo y devuelve el ID o URL.
    """
    token = generate_jwt()
    url = f"{DRIVE_API_BASE_URL}/profile/"

    files = {"file": (file.name, file, file.content_type)}
    headers = {"x-api-key": token}

    response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()
    return response.json()
