import django_filters
from apps.products.models.product_model import Product

class ProductFilter(django_filters.FilterSet):
    """
    Filtro para el modelo Product - por código (coincidencia parcial).
    """

    code = django_filters.CharFilter(
        field_name='code',
        lookup_expr='icontains',  # ahora permite búsqueda parcial
        label='Filtrar por código'
    )

    class Meta:
        model = Product
        fields = ['code']
