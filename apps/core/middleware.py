from django.utils.timezone import now

class RequestTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = now()
        response = self.get_response(request)
        duration = now() - start_time
        print(f'Duration: {duration.total_seconds()} seconds')
        return response

# Crear middleware personalizado que se aplique a todas las solicitudes del proyecto. 
# Por ejemplo, un middleware que mida el tiempo de respuesta o maneje errores globalmente.