from django.urls import path
from apps.comments.api.views.comment_view import (
    comment_list_view, 
    comment_create_view, 
    comment_detail_view
)

urlpatterns = [
    # Comentarios sobre productos
    path('products/<int:product_id>/comments/', comment_list_view, name='product-comment-list'),
    path('products/<int:product_id>/comments/create/', comment_create_view, name='product-comment-create'),
    
    # Comentarios sobre subproductos
    path('products/<int:product_id>/subproducts/<int:subproduct_id>/comments/', comment_list_view, name='subproduct-comment-list'),
    path('products/<int:product_id>/subproducts/<int:subproduct_id>/comments/create/', comment_create_view, name='subproduct-comment-create'),
    
    # Detalles de un comentario
    path('comments/<int:pk>/', comment_detail_view, name='comment-detail'),
]
