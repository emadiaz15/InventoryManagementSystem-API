from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from apps.products.api.views.category import category_list, category_detail, create_category
from apps.products.api.views.types import type_list, type_detail, create_type
from apps.products.api.views.products import product_list, product_detail, create_product  # Incluimos la vista `create_product`

urlpatterns = [
    # Rutas de Categorías
    path('categories/', category_list, name='category-list'),  # Ruta para listar categorías activas
    path('categories/create/', create_category, name='category-create'),  # Ruta para crear una nueva categoría
    path('categories/<int:pk>/', category_detail, name='category-detail'),  # Ruta para detalles de una categoría específica

    # Rutas de Tipos
    path('types/', type_list, name='type-list'),  # Ruta para listar tipos activos
    path('types/create/', create_type, name='type-create'),  # Ruta para crear un nuevo tipo
    path('types/<int:pk>/', type_detail, name='type-detail'),  # Ruta para detalles de un tipo específico

    # Rutas de Productos
    path('products/', product_list, name='product-list'),  # Ruta para listar productos
    path('products/create/', create_product, name='product-create'),  # Ruta para crear un nuevo producto
    path('products/<int:pk>/', product_detail, name='product-detail'),  # Ruta para detalles de un producto específico
]