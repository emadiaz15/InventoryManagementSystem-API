from .base import *
import os
from dotenv import load_dotenv
from datetime import timedelta

# Carga variables de entorno desde un archivo .env en la raíz del proyecto
# Ajusta la ruta a tu .env si es diferente
load_dotenv(BASE_DIR.parent / '.env') # Asume .env está un nivel arriba de donde está manage.py

# --- Clave Secreta ---
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-for-local-dev-only')

# --- Modo Debug ---
DEBUG = True

# --- Hosts Permitidos ---
ALLOWED_HOSTS = ['*'] # Seguro SOLO para local

# --- Base de Datos ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Logging para Desarrollo Local ---
# Correcto: Configurado para mostrar logs en la consola
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': { 'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}', 'style': '{', },
        'simple': { 'format': '[{asctime}] {levelname} {message}', 'style': '{', 'datefmt': '%H:%M:%S' },
    },
    'handlers': { 'console': { 'class': 'logging.StreamHandler', 'formatter': 'simple', }, },
    'root': { 'handlers': ['console'], 'level': 'INFO', },
    'loggers': {
        'django': { 'handlers': ['console'], 'level': 'INFO', 'propagate': False, },
        'django.db.backends': { 'handlers': ['console'], 'level': 'DEBUG', 'propagate': False, },
        'apps': { 'handlers': ['console'], 'level': 'DEBUG', 'propagate': False, },
    }
}

# --- Archivos Estáticos y Multimedia ---
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
# MEDIA_ROOT apunta a una carpeta 'media' fuera del directorio BASE_DIR (un nivel arriba)
# Asegúrate de que esta sea la ubicación deseada y que exista/tenga permisos.
MEDIA_ROOT = BASE_DIR.parent / 'media'

# --- Configuración JWT ---
# Correcto para local
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# --- Configuración CORS ---
# Correcto para permitir tu frontend local
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
]
CORS_ALLOW_HEADERS = [ 'authorization', 'content-type', 'accept', 'origin', 'x-csrftoken', 'x-requested-with', ]
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

# --- Configuración Email (Consola) ---
# Correcto: Muestra emails en la consola para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
