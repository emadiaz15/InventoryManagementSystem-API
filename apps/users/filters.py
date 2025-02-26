# users/filters.py
import django_filters
from .models import User

class UserFilter(django_filters.FilterSet):
    # Filtro para estado (is_active). Por defecto, si no se pasa nada, filtra "Activo".
    is_active = django_filters.BooleanFilter(field_name='is_active', lookup_expr='exact', method='filter_active')

    # Filtro para administrador (is_staff). Permite valores True/False y, si no se envía, no filtra.
    is_staff = django_filters.BooleanFilter(field_name='is_staff', lookup_expr='exact')

    class Meta:
        model = User
        fields = ['name', 'last_name', 'is_active', 'is_staff']

    def filter_active(self, queryset, name, value):
        # Si el parámetro es None o no se envía, forzamos a filtrar activos.
        if value is None:
            return queryset.filter(is_active=True)
        return queryset.filter(**{name: value})
