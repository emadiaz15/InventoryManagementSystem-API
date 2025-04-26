import os
from pathlib import Path
from dotenv import load_dotenv
from celery import Celery

# Cargar variables de entorno
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# Usar DJANGO_SETTINGS_MODULE si ya existe, sino poner local como default
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventory_management.settings.local")

# Crear instancia de Celery
app = Celery("inventory_management")

# Configurar desde settings de Django
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto descubrir tareas de todas las apps instaladas
app.autodiscover_tasks()
