from django.urls import path
from apps.comments.api.views import comment_view as views

urlpatterns = [
    # Ruta para listar los comentarios de un producto o subproducto
    path('comments/<int:product_id>/', views.comment_list_view, name='comment-list'),  # Para productos
    path('comments/<int:product_id>/subproducts/<int:subproduct_id>/', views.comment_list_view, name='comment-list-subproduct'),  # Para subproductos
    
    # Ruta para crear un comentario sobre un producto o subproducto
    path('comments/<int:product_id>/create/', views.comment_create_view, name='comment-create'),  # Para productos
    path('comments/<int:product_id>/subproducts/<int:subproduct_id>/create/', views.comment_create_view, name='comment-create-subproduct'),  # Para subproductos
    
    # Rutas para obtener, actualizar y eliminar un comentario específico
    path('comments/<int:pk>/', views.comment_detail_view, name='comment-detail'),
]
