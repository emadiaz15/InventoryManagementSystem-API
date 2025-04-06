from .base import *
from dotenv import load_dotenv
import os
from datetime import timedelta
import dj_database_url

# Cargar las variables del archivo .env
load_dotenv()  # Cargar las variables de entorno

# --- Clave Secreta ---
# ¡MUY IMPORTANTE! Obtener de variable de entorno en producción. ¡NO hardcodear!
SECRET_KEY = os.environ.get('SECRET_KEY') # Usa os.environ para asegurar que falle si no está definida
if not SECRET_KEY:
     raise ValueError("No se ha definido la variable de entorno SECRET_KEY")

# --- Modo Debug ---
# ¡MUY IMPORTANTE! Siempre False en producción.
DEBUG = False

# --- Hosts Permitidos ---
# ¡NECESARIO CAMBIAR! Lista de tus dominios/subdominios reales donde correrá la app.
# Ejemplo: ALLOWED_HOSTS = ['api.tuinventario.com', 'www.tuinventario.com']
ALLOWED_HOSTS = [
    '.railway.app',
]

# --- Base de Datos ---
# Configuración para PostgreSQL (u otra base de datos de producción)
# usando variables de entorno. dj-database-url simplifica esto.
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}

# --- Seguridad (Configuraciones importantes para HTTPS) ---
# Asumen que tu servidor web (Nginx/Apache) maneja la terminación SSL/TLS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') # Confía en el header X-Forwarded-Proto puesto por el proxy/load balancer
SECURE_SSL_REDIRECT = True # Redirige HTTP a HTTPS (si el proxy no lo hace ya)
SESSION_COOKIE_SECURE = True # Cookies de sesión solo por HTTPS
CSRF_COOKIE_SECURE = True # Cookies CSRF solo por HTTPS
SESSION_COOKIE_HTTPONLY = True # Cookies no accesibles por JavaScript
# HSTS - Fuerza al navegador a usar HTTPS después de la primera visita
SECURE_HSTS_SECONDS = 31536000 # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True # Aplicar a subdominios
SECURE_HSTS_PRELOAD = True # Permitir inclusión en listas de precarga HSTS

# --- Logging para Producción ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False, # Mantener loggers por defecto
    'formatters': {
        'verbose': { # Formato detallado
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file_errors': { # Handler para escribir errores a un archivo
            'level': 'ERROR', # Solo nivel ERROR o superior
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django-error.log'), # ¡NECESARIO CAMBIAR/CONFIGURAR ENV VAR! Ruta REAL en el servidor
            'formatter': 'verbose', # Usa formato detallado
        },
        'console_prod': { # Handler opcional para consola en producción (si usas Docker/PaaS)
             'level': 'INFO', # O WARNING
             'class': 'logging.StreamHandler',
             'formatter': 'verbose',
        },
        # Considera añadir handlers para enviar errores a servicios como Sentry
    },
    'loggers': {
        'django': { # Logger principal de Django
            'handlers': ['file_errors', 'console_prod'], # Envía a archivo y/o consola
            'level': 'INFO', # Captura INFO, WARNING, ERROR, CRITICAL (ERROR va al archivo)
            'propagate': False, # No lo pases al logger raíz
        },
        'apps': { # Logger para tus aplicaciones
             'handlers': ['file_errors', 'console_prod'],
             'level': 'INFO',
             'propagate': False,
        },
        # Puedes añadir más loggers específicos
    },
     'root': { # Logger raíz (captura todo lo no capturado antes)
        'handlers': ['console_prod'], # O solo 'file_errors' si no quieres mucho log
        'level': 'WARNING', # Captura WARNING, ERROR, CRITICAL
    },
}


# --- Configuración JWT (Tiempos de vida más cortos) ---
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15), # Más corto para producción (ej. 15 mins)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7), # Refresco puede ser más largo (ej. 7 días)
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY, # Usa la variable de entorno
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}


# --- Configuración Email (Producción) ---
# ¡NECESARIO CAMBIAR! Usar servicio transaccional (SendGrid, Mailgun, SES) y env vars
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # O un backend específico del servicio
DEFAULT_FROM_EMAIL = os.environ.get('DJANGO_DEFAULT_FROM_EMAIL', 'noreply@tu-dominio-real.com')
EMAIL_HOST = os.environ.get('DJANGO_EMAIL_HOST') # Ej: smtp.sendgrid.net
EMAIL_PORT = int(os.environ.get('DJANGO_EMAIL_PORT', 587)) # Puerto estándar TLS
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_USER') # API Key o usuario
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_PASSWORD') # API Key o contraseña

"""# --- Configuración Celery (Producción) ---
# Usa variables de entorno para las URLs
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0') # Ajusta si Redis no se llama 'redis'
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE"""


# Configuración de CORS
CORS_ALLOWED_ORIGINS = [
    "https://inventarioweb.up.railway.app",  # Frontend
    "https://inventoryapi.up.railway.app",  # Backend
]

CORS_ALLOWED_ORIGIN_REGEXES = []

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


CSRF_TRUSTED_ORIGINS = [
    "https://inventarioweb.up.railway.app",
    "https://inventoryapi.up.railway.app",
]
