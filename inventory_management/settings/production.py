from .base import *

import os
from datetime import timedelta

# Cargar la clave secreta desde las variables de entorno
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# Desactivar DEBUG para producción
DEBUG = False

# Asegúrate de agregar tus dominios reales aquí
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Configuración de la base de datos, asegurándose de cargar las credenciales de las variables de entorno
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Configuraciones de archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Asegúrate de que esta carpeta exista en tu servidor de producción

# Configuraciones de archivos multimedia
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
            'filename': '/path/to/your/logs/django-error.log',  # Cambia esta ruta por la real
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
EMAIL_HOST_USER = 'usuario@tuempresa.com'
EMAIL_HOST_PASSWORD = 'contraseña'
