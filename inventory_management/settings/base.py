from pathlib import Path
from datetime import timedelta
import os # Necesario para algunas configuraciones base


# --- Rutas del Proyecto ---
# BASE_DIR apunta al directorio raíz del proyecto Django (donde está manage.py)
# Ejemplo: /app/
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Definición de Aplicaciones ---
# Aplicaciones estándar de Django
BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
# Aplicaciones de terceros instaladas via pip
THIRD_APPS = [

    'rest_framework',               # Django REST Framework para APIs
    'simple_history',             # Para historial de modelos
    'rest_framework_simplejwt',   # Para autenticación JWT
    'rest_framework_simplejwt.token_blacklist', # Para invalidar refresh tokens
    'drf_spectacular',            # Para generar documentación OpenAPI/Swagger
    'celery',                     # Para tareas asíncronas (si usas)
    'corsheaders',                # Para manejar Cross-Origin Resource Sharing (CORS)
    "csp"                       # Para Content Security Policy
]
# Tus aplicaciones locales
LOCAL_APPS = [
    'apps.products',
    'apps.users',
    'apps.core',
    'apps.cuts',
    'apps.stocks',
    'apps.drive'
]
# Lista completa de aplicaciones instaladas
INSTALLED_APPS = BASE_APPS + THIRD_APPS + LOCAL_APPS

# --- Middleware ---
# Procesan peticiones/respuestas. El orden importa.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',      # Cabeceras de seguridad básicas
    'django.contrib.sessions.middleware.SessionMiddleware', # Manejo de sesiones (si usas)
    'corsheaders.middleware.CorsMiddleware',              # CORS - Debe ir antes de CommonMiddleware
    'django.middleware.common.CommonMiddleware',          # Añade slashes, maneja ETags, etc.
    'django.middleware.csrf.CsrfViewMiddleware',          # Protección CSRF (importante si usas sesiones/formularios)
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Añade request.user
    'django.contrib.messages.middleware.MessageMiddleware', # Sistema de mensajes flash
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Protección contra clickjacking
    'simple_history.middleware.HistoryRequestMiddleware',   # Para que simple_history sepa qué usuario hizo el cambio
    'csp.middleware.CSPMiddleware', # Descomenta si quieres activar CSP globalmente
# 'apps.users.middlewares.BlacklistAccessTokenMiddleware', # Middleware personalizado (comentado)
]

# --- URLs ---
ROOT_URLCONF = 'inventory_management.urls' # Archivo principal de URLs

# --- Templates ---
TEMPLATES = [ # Configuración estándar para plantillas Django (si usas)
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # Directorios extra para buscar plantillas
        'APP_DIRS': True, # Buscar plantillas dentro de las apps
        'OPTIONS': {
            'context_processors': [ # Variables disponibles en todas las plantillas
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --- Servidor WSGI ---
WSGI_APPLICATION = 'inventory_management.wsgi.application' # Punto de entrada para servidores WSGI

# --- Validación de Contraseñas ---
AUTH_PASSWORD_VALIDATORS = [ # Validadores estándar
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# --- Modelo de Usuario Personalizado ---
AUTH_USER_MODEL = 'users.User' # Especifica tu modelo User personalizado

# --- Internacionalización ---
LANGUAGE_CODE = 'es-ar' # Cambiado a Español (Argentina)
TIME_ZONE = 'America/Argentina/Cordoba' # Cambiado a tu zona horaria
USE_I18N = True # Activa internacionalización
USE_TZ = True # Activa soporte de zonas horarias (¡MUY IMPORTANTE!)

# --- Configuración Django REST Framework ---
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',  # Paginador estándar
    'PAGE_SIZE': 10,  # Tamaño de página por defecto
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Autenticación por defecto vía JWT
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # Para documentación automática
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],  # Habilita filtros por defecto
}

# --- Configuración drf-spectacular ---
SPECTACULAR_SETTINGS = {
    'TITLE': 'Inventory Management API',  # Título de tu API
    'DESCRIPTION': 'Documentación de la API para el Sistema de Gestión de Inventario',  # Descripción
    'VERSION': '1.0.0',  # Versión de tu API
    'SERVE_INCLUDE_SCHEMA': False,  # No servir el schema OpenAPI directamente por defecto
    'SECURITY': [{'jwtAuth': []}],  # Configuración de seguridad global (JWT)
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
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' # Tipo de ID autoincremental por defecto

# --- Comportamiento de URLs ---
APPEND_SLASH = False # No añadir slash al final si no está en la URL (preferencia personal)

# --- Logging Base (Consola) ---
# Configuración por defecto que usarán otros entornos si no la sobrescriben.
# Ideal para desarrollo: muestra logs en la consola.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False, # No deshabilita loggers por defecto de Django
    'formatters': { # Define cómo se verán los mensajes de log
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
        'console': { # Define un handler llamado 'console'
            'class': 'logging.StreamHandler', # Envía logs a la salida estándar (consola)
            'formatter': 'simple', # Usa el formato simple definido arriba
        },
    },
    'root': { # Configuración para el logger raíz (captura todo si no hay un logger específico)
        'handlers': ['console'], # Envía los logs capturados al handler 'console'
        'level': 'INFO', # Nivel mínimo para capturar: INFO, WARNING, ERROR, CRITICAL (DEBUG es muy verboso)
    },
    'loggers': { # Configuración específica para loggers nombrados
        'django': { # Para logs generados por Django
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'), # Nivel para Django (puede venir de env var)
            'propagate': False, # No pasa los mensajes al logger raíz (evita duplicados)
        },
         'django.db.backends': { # Para ver las queries SQL (muy útil en debug)
            'handlers': ['console'],
            'level': 'DEBUG', # Cambia a INFO o WARNING si no quieres ver queries
            'propagate': False,
        },
         'apps': { # Un logger para todas tus apps locales
            'handlers': ['console'],
            'level': 'DEBUG', # Muestra todo de tus apps
            'propagate': False,
        },
    }
}


# --- Content Security Policy (CSP) ---
# Define qué recursos puede cargar el navegador (seguridad frontend)
CSP_STYLE_SRC = ("'self'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_SCRIPT_SRC = ("'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "https://cdn.jsdelivr.net", "data:")

# Channels
ASGI_APPLICATION = "inventory_management.asgi.application"

# Redis backend para WebSocket
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.getenv("REDIS_URL", "redis://localhost:6379/0")],
        },
    },
}


CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = "America/Argentina/Buenos_Aires"


DEFAULT_PARSER_CLASSES = [
    'rest_framework.parsers.JSONParser',
    'rest_framework.parsers.MultiPartParser',
    'rest_framework.parsers.FormParser',
]


# URL base de tu servicio FastAPI de Drive (local vs prod lo decides en .env)
DRIVE_API_BASE_URL = os.getenv('DRIVE_API_BASE_URL', 'http://localhost:8001')

# Clave secreta compartida para firmar y verificar JWT
DRIVE_SHARED_SECRET = os.getenv('DRIVE_SHARED_SECRET')
