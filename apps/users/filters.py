import django_filters
from django.db.models import Q
from .models.user_model import User

class UserFilter(django_filters.FilterSet):
    # Filtro para nombre y apellido combinados
    full_name = django_filters.CharFilter(method='filter_full_name')

    # Filtro para estado activo (is_active)
    is_active = django_filters.BooleanFilter(field_name='is_active', lookup_expr='exact', method='filter_active')

    # Filtro para administrador (is_staff)
    is_staff = django_filters.BooleanFilter(field_name='is_staff', lookup_expr='exact')

    # ✅ Filtro para buscar por DNI (permite buscar por coincidencias parciales)
    dni = django_filters.CharFilter(field_name='dni', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['full_name', 'is_active', 'is_staff', 'dni']  # ✅ Agregamos 'dni'

    def filter_full_name(self, queryset, name, value):
        """
        Filtra usuarios buscando cada palabra en los campos name o last_name.
        """
        words = value.split()
        for word in words:
            queryset = queryset.filter(Q(name__icontains=word) | Q(last_name__icontains=word))
        return queryset

    def filter_active(self, queryset, name, value):
        # Si el parámetro no se envía, se filtran solo usuarios activos.
        if value is None:
            return queryset.filter(is_active=True)
        return queryset.filter(**{name: value})
