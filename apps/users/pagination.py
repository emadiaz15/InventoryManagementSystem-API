# apps/users/pagination.py
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    """
    Custom pagination for user lists.
    """
    page_size = 10  # Número de usuarios por página
    page_size_query_param = 'page_size'  # Permitir cambiar el tamaño de la página mediante un parámetro
    max_page_size = 100  # Tamaño máximo de página permitido
