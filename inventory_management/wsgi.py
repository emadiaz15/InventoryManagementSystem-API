import os, logging
from pathlib import Path
from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application

# Cargar .env si existe (solo local)
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# Establece DJANGO_SETTINGS_MODULE si no está ya definido
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings.local')

# Obtiene la aplicación WSGI de Django
application = get_wsgi_application()

logger = logging.getLogger(__name__)
logger.info("🚀 REDIS_URL en producción: %r", os.getenv("REDIS_URL"))