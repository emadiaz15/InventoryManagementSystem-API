# settings/production.py

from .base import *  # incluye INSTALLED_APPS, MIDDLEWARE, ROOT_URLCONF, WSGI_APPLICATION, TIME_ZONE, etc.
import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

# ── BASE_DIR ───────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── SEGURIDAD ──────────────────────────────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("La variable SECRET_KEY no está definida en producción")
DEBUG = False
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',') or []

# ── BASE DE DATOS ──────────────────────────────────────────────
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ImproperlyConfigured("La variable DATABASE_URL no está definida en producción")
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

# ── HTTPS Y SEGURIDAD ──────────────────────────────────────────
SECURE_PROXY_SSL_HEADER        = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT            = True
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True
SESSION_COOKIE_HTTPONLY        = True
SECURE_HSTS_SECONDS            = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD            = True

# ── CSRF Y CORS ────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') or []
CORS_ALLOWED_ORIGINS = os.getenv('DJANGO_CORS_ALLOWED_ORIGINS', '').split(',') or []
CORS_ALLOW_HEADERS    = ['authorization', 'content-type', 'accept', 'origin',
                         'x-csrftoken', 'x-requested-with', 'x-api-key']
CORS_ALLOW_METHODS    = ['GET','POST','PUT','PATCH','DELETE','OPTIONS']
CORS_ALLOW_CREDENTIALS = True

# ── REDIS & CELERY & CHANNELS ──────────────────────────────────
REDIS_URL = os.getenv('REDIS_URL')
if not REDIS_URL:
    raise ImproperlyConfigured("La variable REDIS_URL no está definida en producción")

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [REDIS_URL]},
    },
}

CELERY_BROKER_URL    = os.getenv('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE       = 'America/Argentina/Buenos_Aires'
CELERY_ENABLE_UTC     = False

# ── S3 / MinIO ────────────────────────────────────────────────
AWS_ACCESS_KEY_ID       = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY   = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_ENDPOINT_URL     = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME      = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_PRODUCT_BUCKET_NAME = os.getenv('AWS_PRODUCT_BUCKET_NAME')
AWS_PROFILE_BUCKET_NAME = os.getenv('AWS_PROFILE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN    = os.getenv('AWS_S3_CUSTOM_DOMAIN', None)

AWS_S3_ADDRESSING_STYLE  = 'path'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_SECURE_URLS       = True
AWS_S3_FILE_OVERWRITE    = False
AWS_DEFAULT_ACL          = None
AWS_QUERYSTRING_AUTH     = True

# ── CACHE: Redis con django-redis ─────────────────────────────
from .base import CACHE_TTL

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'TIMEOUT': CACHE_TTL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'inventory_prod',
    }
}

# ── JWT Simple ─────────────────────────────────────────────────
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

# ── LOGGING PRODUCCIÓN ─────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django-error.log',
            'formatter': 'verbose',
        },
        'console_prod': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {'handlers': ['file_errors', 'console_prod'], 'level': 'INFO', 'propagate': False},
        'apps': {'handlers': ['file_errors', 'console_prod'], 'level': 'INFO', 'propagate': False},
    },
    'root': {'handlers': ['console_prod'], 'level': 'WARNING'},
}