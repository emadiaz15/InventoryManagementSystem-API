from django.urls import path
from apps.cuts.api.views.cutting_view import (
    cutting_orders_list_view,
    cutting_order_create_view,
    cutting_order_detail_view
)

urlpatterns = [
    # Ruta para listar todas las órdenes de corte activas
    path('orders/', cutting_orders_list_view, name='cutting_orders_list'),  # Para listar órdenes de corte
    
    # Ruta para crear una nueva orden de corte
    path('orders/create/', cutting_order_create_view, name='cutting_order_create'),  # Para crear una nueva orden

    # Ruta para obtener los detalles, actualizar y eliminar suavemente una orden de corte específica
    path('orders/<int:pk>/', cutting_order_detail_view, name='cutting_order_detail'),  # Detalle, actualizar y soft delete
]
