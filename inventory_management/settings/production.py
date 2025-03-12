from .base import *
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url
import os
# Cargar las variables del archivo .env
load_dotenv()  # Cargar las variables de entorno
# Cargar la clave secreta desde las variables de entorno
SECRET_KEY = os.getenv('SECRET_KEY')

# Desactivar DEBUG para producción
DEBUG = False

# Asegúrate de agregar tus dominios reales aquí
ALLOWED_HOSTS = ['inventarioweb.up.railway.app']
CSRF_TRUSTED_ORIGINS = ['https://inventarioweb.up.railway.app']

# Configuración de la base de datos, cargando las credenciales de las variables de entorno
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}

# Configuración de archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Asegúrate de que esta carpeta exista en tu servidor de producción
STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
# Configuración de archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'  # Asegúrate de que esta carpeta también exista

# Seguridad
SECURE_SSL_REDIRECT = True  # Redirigir todas las solicitudes HTTP a HTTPS
SESSION_COOKIE_SECURE = True  # Asegura que las cookies de sesión solo se envíen a través de HTTPS
CSRF_COOKIE_SECURE = True  # Lo mismo para las cookies CSRF
SESSION_COOKIE_HTTPONLY = True  # Para prevenir el acceso a la cookie a través de JavaScript
SECURE_HSTS_SECONDS = 31536000  # 1 año de HSTS para forzar HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Asegura que también aplique a subdominios
SECURE_HSTS_PRELOAD = True  # Para permitir la precarga de HSTS en navegadores

# Configuración de logging para producción
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/emadiaz/Escritorio/workspace/projects/InventoryManagementSystem/InventoryManagementSystem-API/logs/django-error.log',  # Cambia esta ruta
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
    'SIGNING_KEY': SECRET_KEY,  # Asegúrate de que la variable DJANGO_SECRET_KEY esté configurada en tu entorno de producción
    'VERIFYING_KEY': None,
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
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # Asegúrate de que esté configurado en .env
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # Asegúrate de que esté configurado en .env

# Configuración de Celery con Redis
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Configura Redis como el broker de Celery
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Almacena los resultados de las tareas en Redis
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Configuración de CORS
CORS_ALLOWED_ORIGINS = [
    "https://yourfrontend.com",  # Frontend de producción
]
CORS_ALLOW_HEADERS = [
    'authorization',
    'content-type',
    'accept',
    'origin',
    'x-csrftoken',
    'x-requested-with',
]
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
