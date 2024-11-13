from rest_framework.pagination import PageNumberPagination

class ProductPagination(PageNumberPagination):
    """
    Custom pagination for product lists.
    """
    page_size = 10  # Número de productos por página
    page_size_query_param = 'page_size'  # Permitir cambiar el tamaño de la página mediante un parámetro
    max_page_size = 100  # Tamaño máximo de página permitido
