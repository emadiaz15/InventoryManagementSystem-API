import django_filters
from apps.products.models.type_model import Type 

class TypeFilter(django_filters.FilterSet):
    """
    Filtro para el modelo Type.
    Permite filtrar por:
      - el nombre del tipo (campo "name") de forma parcial, case-insensitive.
      - el nombre de la categoría asociada (campo "category__name") de forma parcial, case-insensitive.
    """
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',  # Contiene, sin importar mayúsculas/minúsculas
        label='Filtrar por nombre del tipo (contiene)'
    )
    category = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains',  # Filtra por nombre de la categoría asociada
        label='Filtrar por nombre de la categoría (contiene)'
    )

    class Meta:
        model = Type
        fields = ['name', 'category']
