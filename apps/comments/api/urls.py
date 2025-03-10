from django.urls import path
from apps.comments.api.views.comment_product_view import (
    comment_product_list_view,
    comment_product_detail_view,
    comment_product_create_view,
)
from apps.comments.api.views.comment_subproduct_view import (
    comment_subproduct_list_view,
    comment_subproduct_detail_view,
    comment_subproduct_create_view,
)

urlpatterns = [
    # Rutas para listar comentarios de productos y subproductos
    path('products/<int:product_pk>/comments/',comment_product_list_view, name='comment-list-product'),  # Para productos
    path('products/<int:product_pk>/subproducts/<int:subproduct_pk>/comments/',comment_subproduct_list_view, name='comment-list-subproduct'),  # Para subproductos

    # Rutas para crear comentarios
    path('products/<int:product_pk>/comments/create/',comment_product_create_view, name='comment-create-product'),  # Para productos
    path('products/<int:product_pk>/subproducts/<int:subproduct_pk>/comments/create/',comment_subproduct_create_view, name='comment-create-subproduct'),  # Para subproductos

    # Rutas para obtener, actualizar y eliminar un comentario específico
    path('products/<int:product_pk>/comments/<int:pk>/',comment_product_detail_view, name='comment-detail-product'),  # Para productos
    path('products/<int:product_pk>/subproducts/<int:subproduct_pk>/comments/<int:pk>/',comment_subproduct_detail_view, name='comment-detail-subproduct'),  # Para subproductos
]
