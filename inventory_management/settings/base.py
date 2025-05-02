from pathlib import Path
from datetime import timedelta
import os

# --- Rutas del Proyecto ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Definición de Aplicaciones ---
BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions'
]

THIRD_APPS = [
    'rest_framework',
    'simple_history',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'celery',
    'corsheaders',
    'csp',
    'sslserver'
]

LOCAL_APPS = [
    'apps.products',
    'apps.users',
    'apps.core',
    'apps.cuts',
    'apps.stocks',
    'apps.drive'
]

INSTALLED_APPS = BASE_APPS + THIRD_APPS + LOCAL_APPS

# --- Middleware ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'csp.middleware.CSPMiddleware',
]

# --- URLs ---
ROOT_URLCONF = 'inventory_management.urls'

# --- Templates ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --- Servidor WSGI ---
WSGI_APPLICATION = 'inventory_management.wsgi.application'

# --- Validación de Contraseñas ---
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# --- Modelo de Usuario Personalizado ---
AUTH_USER_MODEL = 'users.User'

# --- Internacionalización ---
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Cordoba'
USE_I18N = True
USE_TZ = True

# --- Django REST Framework ---
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# --- drf-spectacular ---
SPECTACULAR_SETTINGS = {
    'TITLE': 'Inventory Management API',
    'DESCRIPTION': 'Documentación de la API para el Sistema de Gestión de Inventario',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SECURITY': [{'jwtAuth': []}],
    'SCHEMAS': {
        'jwtAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Use JWT token for authentication',
        }
    }
}

# --- Clave Primaria Automática ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Comportamiento de URLs ---
APPEND_SLASH = False

# --- Logging base ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

# --- Content Security Policy (CSP) ---
CSP_STYLE_SRC = ("'self'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_SCRIPT_SRC = ("'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "https://cdn.jsdelivr.net", "data:")

# --- Channels ---
ASGI_APPLICATION = "inventory_management.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [],
        },
    },
}

# --- Celery ---
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = "America/Argentina/Buenos_Aires"

# --- Parser Classes ---
DEFAULT_PARSER_CLASSES = [
    'rest_framework.parsers.JSONParser',
    'rest_framework.parsers.MultiPartParser',
    'rest_framework.parsers.FormParser',
]
