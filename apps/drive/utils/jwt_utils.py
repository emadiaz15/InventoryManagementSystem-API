import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# --- Validaciones de entorno ---
DRIVE_SHARED_SECRET = getattr(settings, "DRIVE_SHARED_SECRET", None)
if not DRIVE_SHARED_SECRET:
    raise ImproperlyConfigured("Falta DRIVE_SHARED_SECRET en las variables de entorno.")

JWT_TTL = timedelta(hours=8)  # Token válido por 8 horas

def generate_jwt(payload_extra: dict = None) -> str:
    payload = {
        "sub": "django-backend",
        "exp": datetime.utcnow() + JWT_TTL,
    }

    if payload_extra:
        if not isinstance(payload_extra, dict):
            raise TypeError("payload_extra debe ser un dict")
        payload.update(payload_extra)

    return jwt.encode(payload, DRIVE_SHARED_SECRET, algorithm="HS256")
