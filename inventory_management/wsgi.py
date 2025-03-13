import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# Establece el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings.production')

# Obtiene la aplicación WSGI de Django
application = get_wsgi_application()

# Usa WhiteNoise para servir archivos estáticos
application = WhiteNoise(application, root=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'staticfiles'))

# Configura la compresión de los archivos estáticos
application.add_files(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'staticfiles'), prefix='static/')
