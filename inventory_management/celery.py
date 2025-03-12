from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establece el módulo de configuración para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')

app = Celery('inventory_management')

# Usamos la configuración de Django para Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar tareas de todas las aplicaciones registradas
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

# Configuración de Celery para usar Redis como broker
app.conf.broker_url = 'redis://redis:6379/0'  # Usar el nombre del servicio de Redis
app.conf.result_backend = 'redis://redis:6379/0'  # Almacenar los resultados en Redis
app.conf.accept_content = ['json']
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.timezone = 'UTC'
app.conf.broker_connection_retry_on_startup = True