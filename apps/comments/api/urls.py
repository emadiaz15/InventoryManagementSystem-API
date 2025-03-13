from django.urls import path
from apps.comments.api.views.comment_product_view import (
    comment_product_create_view,
    comment_product_list_view,
    comment_product_detail_view,
)
from apps.comments.api.views.comment_subproduct_view import (
    comment_subproduct_create_view,
    comment_subproduct_list_view,
    comment_subproduct_detail_view,
)

urlpatterns = [
    # CRUD de comentarios para productos
    path('products/<int:prod_pk>/comments/create/', comment_product_create_view, name='comment-create-product'),
    path('products/<int:prod_pk>/comments/', comment_product_list_view, name='comment-list-product'),
    path('products/<int:prod_pk>/comments/<int:comment_pk>/', comment_product_detail_view, name='comment-detail-product'),
    
    # CRUD de comentarios para subproductos
    path('products/<int:prod_pk>/subproducts/<int:subp_pk>/comments/create/', comment_subproduct_create_view, name='comment-create-subproduct'),
    path('products/<int:prod_pk>/subproducts/<int:subp_pk>/comments/', comment_subproduct_list_view, name='comment-list-subproduct'),
    path('products/<int:prod_pk>/subproducts/<int:subp_pk>/comments/<int:comment_subp_pk>/', comment_subproduct_detail_view, name='comment-detail-subproduct'),
]