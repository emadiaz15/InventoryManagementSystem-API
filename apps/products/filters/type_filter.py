import django_filters
from apps.products.models.type_model import Type 

class TypeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    category = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains'
    )
    category_id = django_filters.NumberFilter(
        field_name='category_id',
        label='Filtrar por ID de la categoría'
    )

    class Meta:
        model = Type
        fields = ['name', 'category', 'category_id']
