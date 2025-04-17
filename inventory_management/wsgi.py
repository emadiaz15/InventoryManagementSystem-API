import os
from django.core.wsgi import get_wsgi_application

# Establece el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings.production')

# Obtiene la aplicación WSGI de Django
application = get_wsgi_application()

