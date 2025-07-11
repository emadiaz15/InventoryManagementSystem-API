from .base import *
import os
from dotenv import load_dotenv
from datetime import timedelta

# Cargar variables desde .env.local
load_dotenv(BASE_DIR.parent / '.env.local')

# --- Seguridad ---
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-for-local-dev-only')
DEBUG = True
ALLOWED_HOSTS = ['*']

# --- Base de datos ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Archivos estáticos y media ---
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / 'media'

# --- Almacenamiento S3 (MinIO) ---
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_PRODUCT_BUCKET_NAME = os.getenv('AWS_PRODUCT_BUCKET_NAME')
AWS_PROFILE_BUCKET_NAME = os.getenv('AWS_PROFILE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False

# ←─ Añadido para forzar HTTP en dev y apuntar al dominio público correcto ─→
AWS_S3_SECURE_URLS   = False
AWS_S3_CUSTOM_DOMAIN = os.getenv('MINIO_PUBLIC_URL')

# --- Logging local ---
LOGGING['loggers']['django']['level'] = os.getenv('DJANGO_LOG_LEVEL', 'INFO')
LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# --- CORS local ---
CORS_ALLOWED_ORIGINS = os.getenv("DJANGO_CORS_ALLOWED_ORIGINS", "").split(",")
CORS_ALLOW_HEADERS = ['authorization', 'content-type', 'accept', 'origin', 'x-csrftoken', 'x-requested-with', 'x-api-key']
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

# --- Email local ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- JWT ---
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

# --- Redis & Celery ---
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

CHANNEL_LAYERS["default"]["CONFIG"]["hosts"] = [REDIS_URL]
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# --- API Drive compartido ---
DRIVE_SHARED_SECRET = os.getenv('DRIVE_SHARED_SECRET', 'fallback_dev_secret')

MINIO_PUBLIC_URL = os.getenv("MINIO_PUBLIC_URL", AWS_S3_ENDPOINT_URL)
