import django_filters
from apps.products.models.subproduct_model import Subproduct

class SubproductFilter(django_filters.FilterSet):
    """
    Filtro para Subproduct que permite 
    — además de otros filtros que quieras añadir —
    filtrar por su campo 'status' (activo/inactivo).
    """
    status = django_filters.BooleanFilter(
        field_name='status',
        label='Solo activos',
        help_text='True para activos, False para inactivos'
    )

    class Meta:
        model = Subproduct
        fields = ['status']
        # aquí podrías añadir más campos si en el futuro quieres filtrar por brand, location, etc.
