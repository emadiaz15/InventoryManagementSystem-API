from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from apps.products.api.views.category import category_list, category_detail
from apps.products.api.views.types import type_list, type_detail, create_type
from apps.products.api.views.products import product_list, product_detail

urlpatterns = [
    # Rutas de Categorías
    path('categories/', category_list, name='category-list'),
    path('categories/<int:pk>/', category_detail, name='category-detail'),

 # Rutas de Tipos
    path('types/', type_list, name='type-list'),  # Ruta para listar tipos activos
    path('types/create/', create_type, name='type-create'),  # Nueva ruta para crear un tipo
    path('types/<int:pk>/', type_detail, name='type-detail'),  # Ruta para detalles de un tipo específico

    # Rutas de Productos
    path('products/', product_list, name='product-list'),
    path('products/<int:pk>/', product_detail, name='product-detail'),  # Corrección en el nombre de la ruta a plural
]

# Añadir soporte para sufijos de formatos (e.g., /products.json)
urlpatterns = format_suffix_patterns(urlpatterns)
