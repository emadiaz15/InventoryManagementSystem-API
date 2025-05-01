from django.urls import path
from apps.products.api.views.category_view import category_list, category_detail, create_category
from apps.products.api.views.types_view import type_list, type_detail, create_type
from apps.products.api.views.products_view import product_list, product_detail, create_product
from apps.products.api.views.subproducts_view import subproduct_list, create_subproduct, subproduct_detail
from apps.products.api.views.product_image_proxy import (
    product_image_upload_view,
    product_image_list_view,
    product_image_delete_view,
)

urlpatterns = [
    # --- Categorías ---
    path('categories/', category_list, name='category-list'),
    path('categories/create/', create_category, name='category-create'),
    path('categories/<int:category_pk>/', category_detail, name='category-detail'),

    # --- Tipos ---
    path('types/', type_list, name='type-list'),
    path('types/create/', create_type, name='type-create'),
    path('types/<int:type_pk>/', type_detail, name='type-detail'),

    # --- Productos ---
    path('products/', product_list, name='product-list'),
    path('products/create/', create_product, name='product-create'),
    path('products/<int:prod_pk>/', product_detail, name='product-detail'),

    # --- Subproductos ---
    path('products/<int:prod_pk>/subproducts/', subproduct_list, name='subproduct-list'),
    path('products/<int:prod_pk>/subproducts/create/', create_subproduct, name='subproduct-create'),
    path('products/<int:prod_pk>/subproducts/<int:subp_pk>/', subproduct_detail, name='subproduct-detail'),

    # --- Imágenes de Productos (lo que existe actualmente) ---
    path('products/<str:product_id>/images/', product_image_list_view, name='product-image-list'),
    path('products/<str:product_id>/images/upload/', product_image_upload_view, name='product-image-upload'),
    path('products/<str:product_id>/images/<str:file_id>/delete/', product_image_delete_view, name='product-image-delete'),
]
