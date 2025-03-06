from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from apps.products.api.views.category_view import category_list, category_detail, create_category
from apps.products.api.views.types_view import type_list, type_detail, create_type
from apps.products.api.views.products_view import product_list, product_detail, create_product
from apps.products.api.views.subproducts import subproduct_list, create_subproduct, subproduct_detail

urlpatterns = [
    # Rutas de Categorías
    path('categories/', category_list, name='category-list'),
    path('categories/create/', create_category, name='category-create'),
    path('categories/<int:pk>/', category_detail, name='category-detail'),

    # Rutas de Tipos
    path('types/', type_list, name='type-list'),
    path('types/create/', create_type, name='type-create'),
    path('types/<int:pk>/', type_detail, name='type-detail'),

    # Rutas de Productos
    path('products/', product_list, name='product-list'),
    path('products/create/', create_product, name='product-create'),
    path('products/<int:pk>/', product_detail, name='product-detail'),

    # Rutas de SubProductos (anidadas en Producto)
    path('products/<int:product_pk>/subproducts/', subproduct_list, name='subproduct-list'),  # Listar subproductos de un producto
    path('products/<int:product_pk>/subproducts/create/', create_subproduct, name='subproduct-create'),  # Crear un nuevo subproducto en un producto
    path('products/<int:product_pk>/subproducts/<int:pk>/', subproduct_detail, name='subproduct-detail'),  # Detalles de un subproducto específico
]