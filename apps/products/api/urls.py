from django.urls import path
from apps.products.api.views.category_view import category_list, category_detail, create_category
from apps.products.api.views.types_view import type_list, type_detail, create_type
from apps.products.api.views.products_view import product_list, product_detail, create_product
from apps.products.api.views.subproducts_view import subproduct_list, create_subproduct, subproduct_detail
from apps.products.api.views.product_files_view import (
    product_file_upload_view,
    product_file_list_view,
    product_file_delete_view,
    product_file_download_view
)
from apps.products.api.views.subproduct_files_view import (
    subproduct_file_upload_view,
    subproduct_file_list_view,
    subproduct_file_delete_view,
    subproduct_file_download_view
)

urlpatterns = [
    # --- 📂 Categorías ---
    path('categories/', category_list, name='category-list'),
    path('categories/create/', create_category, name='category-create'),
    path('categories/<int:category_pk>/', category_detail, name='category-detail'),

    # --- 🏷️ Tipos ---
    path('types/', type_list, name='type-list'),
    path('types/create/', create_type, name='type-create'),
    path('types/<int:type_pk>/', type_detail, name='type-detail'),

    # --- 📦 Productos ---
    path('products/', product_list, name='product-list'),
    path('products/create/', create_product, name='product-create'),
    path('products/<int:prod_pk>/', product_detail, name='product-detail'),

    # --- 🔄 Subproductos ---
    path('products/<int:prod_pk>/subproducts/', subproduct_list, name='subproduct-list'),
    path('products/<int:prod_pk>/subproducts/create/', create_subproduct, name='subproduct-create'),
    path('products/<int:prod_pk>/subproducts/<int:subp_pk>/', subproduct_detail, name='subproduct-detail'),

    # --- 🎞️ Archivos Multimedia de Productos ---
    path('products/<str:product_id>/files/', product_file_list_view, name='product-file-list'),
    path('products/<str:product_id>/files/upload/', product_file_upload_view, name='product-file-upload'),
    path('products/<str:product_id>/files/<str:file_id>/delete/', product_file_delete_view, name='product-file-delete'),
    path('products/<str:product_id>/files/<str:file_id>/download/', product_file_download_view, name='product-file-download'),

    # --- 🎞️ Archivos Multimedia de Subproductos ---
    path('products/<str:product_id>/subproducts/<str:subproduct_id>/files/',subproduct_file_list_view,name='subproduct-file-list'),
    path('products/<str:product_id>/subproducts/<str:subproduct_id>/files/upload/',subproduct_file_upload_view,name='subproduct-file-upload'),
    path('products/<str:product_id>/subproducts/<str:subproduct_id>/files/<str:file_id>/delete/',subproduct_file_delete_view,name='subproduct-file-delete'),
    path('products/<str:product_id>/subproducts/<str:subproduct_id>/files/<str:file_id>/download/',subproduct_file_download_view,name='subproduct-file-download'),
]
