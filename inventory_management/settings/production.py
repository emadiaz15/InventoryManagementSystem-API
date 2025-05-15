from .base import *
import os
from dotenv import load_dotenv
import dj_database_url
from datetime import timedelta

# Cargar variables de entorno
load_dotenv(BASE_DIR.parent / '.env.production')

# --- Clave Secreta ---
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("No se ha definido la variable de entorno SECRET_KEY")

# --- Debug ---
DEBUG = False

# --- Allowed Hosts ---
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')

# --- Base de datos ---
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}

# --- Static files ---
STATIC_URL = '/static/'

# --- Seguridad producción ---
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# --- CSRF trusted origins ---
CSRF_TRUSTED_ORIGINS = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')

# --- CORS ---
CORS_ALLOWED_ORIGINS = os.getenv('DJANGO_CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOWED_ORIGIN_REGEXES = []
CORS_ALLOW_HEADERS = [
    'authorization', 'content-type', 'accept', 'origin', 'x-csrftoken', 'x-requested-with', 'x-api-key'
]
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

# --- Redis Channels y Celery ---
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.getenv("REDIS_URL")],
        },
    },
}

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

# --- Drive API ---
DRIVE_API_BASE_URL = os.getenv('DRIVE_API_BASE_URL')
DRIVE_SHARED_SECRET = os.getenv('DRIVE_SHARED_SECRET')

# --- Logging Producción ---
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
        'django': {
            'handlers': ['file_errors', 'console_prod'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file_errors', 'console_prod'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console_prod'],
        'level': 'WARNING',
    },
}

# --- Simple JWT producción ---
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
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

# --- Email Producción (opcional) ---
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# DEFAULT_FROM_EMAIL = os.getenv('DJANGO_DEFAULT_FROM_EMAIL', 'noreply@tu-dominio-real.com')
# EMAIL_HOST = os.getenv('DJANGO_EMAIL_HOST')
# EMAIL_PORT = int(os.getenv('DJANGO_EMAIL_PORT', 587))
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL_USER')
# EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_PASSWORD')
