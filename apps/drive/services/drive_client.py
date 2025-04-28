import os
import requests
import jwt
from datetime import datetime, timedelta

DRIVE_API_BASE_URL = os.getenv("DRIVE_API_BASE_URL")
SHARED_SECRET = os.getenv("DRIVE_SHARED_SECRET")


def generate_jwt():
    payload = {
        "sub": "django-backend",
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    return jwt.encode(payload, SHARED_SECRET, algorithm="HS256")


def upload_profile_image(file):
    """
    Sube una imagen de perfil a la API externa.
    """
    token = generate_jwt()
    url = f"{DRIVE_API_BASE_URL}/profile/"
    files = {"file": (file.name, file, file.content_type)}
    headers = {"x-api-key": token}

    response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()
    return response.json()
