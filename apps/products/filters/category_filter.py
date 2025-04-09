import django_filters
from apps.products.models.category_model import Category

class CategoryFilter(django_filters.FilterSet):
    """
    Filtro para el modelo Category - SOLO por nombre.
    Permite filtrar por nombre (parcial, insensible a mayúsculas/minúsculas).
    """

    # --- ÚNICO Filtro Definido: name ---
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains', # 'icontains' = case-insensitive contains
        label='Filtrar por nombre (contiene)'
    )

    # --- Filtro 'status' ELIMINADO ---
    # status = django_filters.BooleanFilter(...) # Eliminado

    class Meta:
        model = Category
        # Ahora solo referencia 'name'
        fields = ['name']
