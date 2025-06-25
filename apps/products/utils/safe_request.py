from django.http import Http404
from requests.exceptions import RequestException
import requests

def safe_request(func, *args, **kwargs):
    """
    Ejecuta una función de red de forma segura, capturando errores.
    """
    try:
        return func(*args, **kwargs)
    except requests.HTTPError as e:
        status_code = getattr(e.response, 'status_code', None)
        if status_code == 404:
            raise Http404("Recurso no encontrado.")
        raise Http404(f"Error en solicitud HTTP: {e}")
    except RequestException as e:
        raise Http404(f"Error de conexión: {e}")
    except Exception as e:
        raise Http404(f"Error inesperado: {e}")
