# settings/production.py

from .base import *
import os
import dj_database_url
from datetime import timedelta
from pathlib import Path

# ── BASE_DIR ───────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── SEGURIDAD ──────────────────────────────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("La variable SECRET_KEY no está definida en producción")
DEBUG = False
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',') or []

# ── BASE DE DATOS ──────────────────────────────────────────────
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("La variable DATABASE_URL no está definida en producción")
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

# ── ARCHIVOS ESTÁTICOS ─────────────────────────────────────────
STATIC_URL = '/static/'

# ── S3 / MINIO ─────────────────────────────────────────────────
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_ENDPOINT_URL     = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_ACCESS_KEY_ID       = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY   = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_PRODUCT_BUCKET_NAME = os.getenv('AWS_PRODUCT_BUCKET_NAME')
AWS_PROFILE_BUCKET_NAME = os.getenv('AWS_PROFILE_BUCKET_NAME')
AWS_S3_REGION_NAME      = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_FILE_OVERWRITE   = False
AWS_DEFAULT_ACL         = None
AWS_QUERYSTRING_AUTH    = False
AWS_S3_CUSTOM_DOMAIN    = os.getenv('MINIO_PUBLIC_ENDPOINT')
AWS_S3_ADDRESSING_STYLE = os.getenv('AWS_S3_ADDRESSING_STYLE', 'path')

# URL pública de MinIO para presigned URLs
MINIO_PUBLIC_URL      = os.getenv('MINIO_PUBLIC_ENDPOINT', AWS_S3_CUSTOM_DOMAIN)
AWS_S3_CUSTOM_DOMAIN  = MINIO_PUBLIC_URL

# ── HTTPS Y SEGURIDAD ──────────────────────────────────────────
SECURE_PROXY_SSL_HEADER       = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT           = True
SESSION_COOKIE_SECURE         = True
CSRF_COOKIE_SECURE            = True
SESSION_COOKIE_HTTPONLY       = True
SECURE_HSTS_SECONDS           = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS= True
SECURE_HSTS_PRELOAD           = True

# ── CSRF Y CORS ────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS      = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') or []
CORS_ALLOWED_ORIGINS      = os.getenv('DJANGO_CORS_ALLOWED_ORIGINS', '').split(',') or []
CORS_ALLOW_HEADERS        = [
    'authorization', 'content-type', 'accept', 'origin',
    'x-csrftoken', 'x-requested-with', 'x-api-key'
]
CORS_ALLOW_METHODS        = ['GET','POST','PUT','PATCH','DELETE','OPTIONS']
CORS_ALLOW_CREDENTIALS    = True

# ── REDIS Y CELERY ─────────────────────────────────────────────
REDIS_URL = os.getenv('REDIS_URL')
if not REDIS_URL:
    raise ValueError("La variable REDIS_URL no está definida en producción")

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [REDIS_URL]},
    },
}
CELERY_BROKER_URL     = os.getenv('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)

# ── CACHE: Redis o memoria local ───────────────────────────────
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-inventory-production",
        }
    }

# ── JWT ────────────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
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
            'filename': os.path.join(BASE_DIR, 'django-error.log'),
            'formatter': 'verbose',
        },
        'console_prod': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {'handlers': ['file_errors','console_prod'], 'level': 'INFO', 'propagate': False},
        'apps':   {'handlers': ['file_errors','console_prod'], 'level': 'INFO', 'propagate': False},
    },
    'root': {'handlers': ['console_prod'], 'level': 'WARNING'},
}
