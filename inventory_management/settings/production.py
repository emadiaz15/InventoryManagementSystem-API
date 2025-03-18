from .base import *
from dotenv import load_dotenv
import os
from datetime import timedelta
import dj_database_url

# Cargar las variables del archivo .env
load_dotenv()  # Cargar las variables de entorno
SECRET_KEY = os.getenv('SECRET_KEY')

# Configuración básica
DEBUG = False


# Configuración de la base de datos (sin utilizar dj_database_url, usando variables separadas)
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}

# Seguridad
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_HSTS_SECONDS = 31536000  # 1 año de HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configuración de logging para producción
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django-error.log'),  # Usa BASE_DIR para una ruta relativa
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Configuración para JWT (JSON Web Tokens)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
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

# Configuración para el envío de correos electrónicos
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@tuempresa.com'
EMAIL_HOST = 'smtp.tuempresa.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

"""# Configuración de Celery con Redis
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'"""

# Configuración de CORS
CORS_ALLOWED_ORIGINS = [
    "https://inventarioweb.up.railway.app",
]
CORS_ALLOWED_ORIGIN_REGEXES = []  # Opcional: puedes omitir esta línea si no necesitas regex

CORS_ALLOW_HEADERS = [
    'authorization', 'content-type', 'accept', 'origin', 'x-csrftoken', 'x-requested-with',
]
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

# Directorio donde se almacenarán los archivos estáticos después de ejecutar collectstatic
STATIC_URL = '/static/'

"""# Directorio para los archivos estáticos que el proyecto puede servir localmente
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '/staticfiles'),  # Asegúrate de que esta ruta sea correcta
]

# El directorio donde Django almacenará todos los archivos estáticos para producción (cuando uses collectstatic)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuración de WhiteNoise para servir los archivos estáticos en producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'"""

ALLOWED_HOSTS = [
    '.railway.app',
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True