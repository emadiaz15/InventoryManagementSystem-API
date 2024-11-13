from django.urls import path
from apps.cuts.api.views.cutting import cutting_orders_view, cutting_order_detail_view

urlpatterns = [
    # Ruta para listar todas las órdenes de corte y crear una nueva
    path('orders/', cutting_orders_view, name='cutting_orders'),  # Para listar y crear órdenes
    
    # Ruta para el detalle, actualización y eliminación de una orden de corte específica
    path('orders/<int:pk>/', cutting_order_detail_view, name='cutting_order_detail'),  # Detalle, actualizar y eliminar
]
