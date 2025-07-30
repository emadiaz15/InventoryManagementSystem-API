# apps/products/filters/product_filter.py

import django_filters
from django.core.exceptions import ValidationError
from apps.products.models.product_model import Product


class ProductFilter(django_filters.FilterSet):
    """
    Filtro para el modelo Product:
    - code: búsqueda parcial por prefijo (startswith)
    - category/type: búsqueda insensible a mayúsculas (icontains)
    """

    code = django_filters.CharFilter(
        field_name='code',
        lookup_expr='startswith',  # permite filtrar como "4" => "401"
        label='Filtrar por código (parcial)'
    )

    category = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains',  # búsqueda parcial sin distinción mayúsculas
        label='Filtrar por categoría (nombre parcial)'
    )

    type = django_filters.CharFilter(
        field_name='type__name',
        lookup_expr='icontains',
        label='Filtrar por tipo (nombre parcial)'
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        # Validar que code tenga solo dígitos (no letras o símbolos)
        if data and 'code' in data and data['code'] != '':
            if not str(data['code']).isdigit():
                raise ValidationError({"code": f"'{data['code']}' no es un código válido. Debe contener solo números."})
        super().__init__(data, queryset, request=request, prefix=prefix)

    class Meta:
        model = Product
        fields = ['code', 'category', 'type']
