from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from apps.products.api.views.categories.category_list import category_list
from apps.products.api.views.categories.category_detail import category_detail
from apps.products.api.views.types.type_detail import type_detail
from apps.products.api.views.types.type_list import type_list
from apps.products.api.views.products.product_list import product_list
from apps.products.api.views.products.product_detail import product_detail

urlpatterns = [
    # Rutas de Categorías
    path('categories/', category_list, name='category-list'),
    path('categories/<int:pk>/', category_detail, name='category-detail'),

    # Rutas de Tipos
    path('types/', type_list, name='type-list'),
    path('types/<int:pk>/', type_detail, name='type-detail'),

    # Rutas de Productos
    path('products/', product_list, name='product-list'),
    path('products/<int:pk>/', product_detail, name='product-detail'),  # Corrección en el nombre de la ruta a plural
]

# Añadir soporte para sufijos de formatos (e.g., /products.json)
urlpatterns = format_suffix_patterns(urlpatterns)
