from .base import *
import os
from dotenv import load_dotenv
from datetime import timedelta

# Cargar variables de entorno desde .env.local
load_dotenv(BASE_DIR.parent / '.env.local')

# --- Clave Secreta ---
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-for-local-dev-only')

# --- Modo Debug ---
DEBUG = True

# --- Hosts Permitidos ---
ALLOWED_HOSTS = ['*']

# --- Base de Datos ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Archivos Estáticos y Multimedia ---
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / 'media'

# --- Logging para Desarrollo Local ---
LOGGING['loggers']['django']['level'] = os.getenv('DJANGO_LOG_LEVEL', 'INFO')
LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# --- Configuración CORS ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
]
CORS_ALLOW_HEADERS = ['authorization', 'content-type', 'accept', 'origin', 'x-csrftoken', 'x-requested-with']
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

# --- Configuración Email ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- Configuración JWT ---
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

# --- Websocket Redis (Channels) ---
CHANNEL_LAYERS["default"]["CONFIG"]["hosts"] = [os.getenv("REDIS_URL", "redis://localhost:6379/0")]

# --- Celery ---
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# --- Drive API ---
DRIVE_API_BASE_URL = os.getenv('DRIVE_API_BASE_URL', 'http://localhost:8001')
DRIVE_SHARED_SECRET = os.getenv('DRIVE_SHARED_SECRET')
