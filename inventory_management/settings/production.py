from .base import *

import os
from datetime import timedelta
import dj_database_url # Necesitarás instalar dj-database-url: pip install dj-database-url

# --- Clave Secreta ---
# ¡MUY IMPORTANTE! Obtener de variable de entorno en producción. ¡NO hardcodear!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') # Usa os.environ para asegurar que falle si no está definida
if not SECRET_KEY:
     raise ValueError("No se ha definido la variable de entorno DJANGO_SECRET_KEY")

# --- Modo Debug ---
# ¡MUY IMPORTANTE! Siempre False en producción.
DEBUG = False

# --- Hosts Permitidos ---
# ¡NECESARIO CAMBIAR! Lista de tus dominios/subdominios reales donde correrá la app.
# Ejemplo: ALLOWED_HOSTS = ['api.tuinventario.com', 'www.tuinventario.com']
ALLOWED_HOSTS_ENV = os.environ.get('DJANGO_ALLOWED_HOSTS')
if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS = ALLOWED_HOSTS_ENV.split(',') # Permite definir hosts separados por comas en la env var
else:
    ALLOWED_HOSTS = [] # O define un default si prefieres
    # raise ValueError("No se ha definido la variable de entorno DJANGO_ALLOWED_HOSTS")

# --- Base de Datos ---
# Configuración para PostgreSQL (u otra base de datos de producción)
# usando variables de entorno. dj-database-url simplifica esto.
DATABASE_URL = os.environ.get('DATABASE_URL') # Ejemplo: postgres://user:password@host:port/dbname
if not DATABASE_URL:
     raise ValueError("No se ha definido la variable de entorno DATABASE_URL")
DATABASES = {
    # Usa dj_database_url para parsear la URL y configurar la conexión
    'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600, ssl_require=True) # ssl_require=True recomendado para producción
}

# --- Archivos Estáticos (ej. para Admin) ---
# Servidos por Nginx o similar en producción. `collectstatic` los reúne aquí.
STATIC_URL = '/static/' # URL pública
STATIC_ROOT = BASE_DIR.parent / 'staticfiles_collected' # Carpeta REAL en el servidor donde collectstatic los copia
# Asegúrate de que esta carpeta sea escribible por el proceso que corre collectstatic
# y legible por el servidor web (Nginx).

# --- Archivos Multimedia (subidos por usuarios) ---
# También servidos por Nginx o S3/similar en producción.
MEDIA_URL = '/media/' # URL pública
MEDIA_ROOT = BASE_DIR.parent / 'media' # Carpeta REAL en el servidor donde se guardan los archivos
# Asegúrate de que esta carpeta sea escribible por el proceso de Django
# y legible por el servidor web (Nginx).

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
            'filename': os.environ.get('DJANGO_LOG_PATH', '/var/log/django/django-error.log'), # ¡NECESARIO CAMBIAR/CONFIGURAR ENV VAR! Ruta REAL en el servidor
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

# --- Configuración Celery (Producción) ---
# Usa variables de entorno para las URLs
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0') # Ajusta si Redis no se llama 'redis'
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# ============== FIN ARCHIVO: settings/production.py ==============