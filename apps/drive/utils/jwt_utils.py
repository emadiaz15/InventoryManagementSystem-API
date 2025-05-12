import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.exceptions import AuthenticationFailed
from django.http import HttpRequest

# --- 🔐 Validación y carga de clave secreta ---
DRIVE_SHARED_SECRET = getattr(settings, "DRIVE_SHARED_SECRET", None)
if not DRIVE_SHARED_SECRET:
    raise ImproperlyConfigured("Falta DRIVE_SHARED_SECRET en las variables de entorno.")

# --- ⏳ Tiempo de vida del token ---
JWT_TTL = timedelta(hours=8)

def generate_jwt(payload_extra: dict = None) -> str:
    """
    Genera un token JWT firmado con la clave compartida con el microservicio FastAPI.
    El token incluye `sub` y `exp` por defecto.
    """
    base_payload = {
        "sub": "django-backend",
        "exp": datetime.utcnow() + JWT_TTL,
    }

    if payload_extra:
        if not isinstance(payload_extra, dict):
            raise TypeError("payload_extra debe ser un dict")
        base_payload.update(payload_extra)

    return jwt.encode(base_payload, DRIVE_SHARED_SECRET, algorithm="HS256")


def extract_bearer_token(request: HttpRequest, *, token_type: str = "access") -> str:
    """
    Extrae el token Bearer desde el header Authorization del request.

    Args:
        request (HttpRequest): El request de Django.
        token_type (str): Puede ser "access" o "fastapi".

    Returns:
        str: El token extraído o generado.

    Raises:
        AuthenticationFailed: Si no se encuentra el token esperado.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.lower().startswith("bearer "):
        raise AuthenticationFailed("Token Bearer no proporcionado.")

    if token_type == "access":
        return auth_header.split(" ")[1]

    elif token_type == "fastapi":
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed("Usuario no autenticado.")
        return generate_jwt({"user_id": request.user.id})

    raise AuthenticationFailed("Tipo de token inválido.")
