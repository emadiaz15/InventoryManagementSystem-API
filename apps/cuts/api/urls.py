from django.urls import path
from apps.cuts.api.views.cutting_view import (
    cutting_orders_list_view,
    cutting_order_create_view,
    cutting_order_detail_view
)

urlpatterns = [
    # ✅ Ruta para listar todas las órdenes de corte activas
    path('cutting-orders/', cutting_orders_list_view, name='cutting_orders_list'),

    # ✅ Ruta para crear una nueva orden de corte
    path('cutting-orders/create/', cutting_order_create_view, name='cutting_order_create'),

    # ✅ Ruta para obtener, actualizar y eliminar suavemente una orden de corte específica
    path('cutting-orders/<int:pk>/', cutting_order_detail_view, name='cutting_order_detail'),
]
