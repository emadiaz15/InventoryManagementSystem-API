from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)

class RequestTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = now()
        response = self.get_response(request)
        duration = now() - start_time
        logger.info(f'Duration: {duration.total_seconds()} seconds')
        return response

# Crear middleware personalizado que se aplique a todas las solicitudes del proyecto. 
# Por ejemplo, un middleware que mida el tiempo de respuesta o maneje errores globalmente.

# Middleware personalizado
class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            content_length = len(response.content)  # Este es el acceso que causa el error
        except Exception as e:
            logger.error(f"Error al acceder a la respuesta: {e}")
        return response
