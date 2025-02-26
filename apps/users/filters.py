import django_filters
from django.db.models import Q
from .models import User

class UserFilter(django_filters.FilterSet):
    # Nuevo filtro que combina name y last_name
    full_name = django_filters.CharFilter(method='filter_full_name')

    # Filtro para estado (is_active). Por defecto, si no se pasa nada, filtra "Activo".
    is_active = django_filters.BooleanFilter(field_name='is_active', lookup_expr='exact', method='filter_active')
    
    # Filtro para administrador (is_staff). Permite valores True/False y, si no se envía, no filtra.
    is_staff = django_filters.BooleanFilter(field_name='is_staff', lookup_expr='exact')

    class Meta:
        model = User
        # Reemplazamos los filtros 'name' y 'last_name' por full_name
        fields = ['full_name', 'is_active', 'is_staff']

    def filter_full_name(self, queryset, name, value):
        """
        Filtra usuarios buscando cada palabra en el input en los campos name o last_name.
        La búsqueda es case-insensitive (icontains).
        """
        # Separa el input en palabras
        words = value.split()
        # Para cada palabra, filtra en el queryset
        for word in words:
            queryset = queryset.filter(
                Q(name__icontains=word) | Q(last_name__icontains=word)
            )
        return queryset

    def filter_active(self, queryset, name, value):
        # Si el parámetro es None, se filtran los usuarios activos.
        if value is None:
            return queryset.filter(is_active=True)
        return queryset.filter(**{name: value})
