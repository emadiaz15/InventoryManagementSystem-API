import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.asgi import get_asgi_application

# Cargar variables de entorno
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# Usar DJANGO_SETTINGS_MODULE si existe, sino usar local por defecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings.local')

application = get_asgi_application()
