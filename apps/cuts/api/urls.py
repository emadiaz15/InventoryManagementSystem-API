from django.urls import path
from apps.cuts.api.views.cutting_view import (
    cutting_order_list,
    cutting_order_create,
    cutting_order_detail,
)

urlpatterns = [
    # ✅ Ruta para listar todas las órdenes de corte activas
    path('cutting-orders/', cutting_order_list, name='cutting_orders_list'),

    # ✅ Ruta para crear una nueva orden de corte
    path('cutting-orders/create/', cutting_order_create, name='cutting_order_create'),

    # ✅ Ruta para obtener, actualizar y eliminar suavemente una orden de corte específica
    path('cutting-orders/<int:cuts_pk>/', cutting_order_detail, name='cutting_order_detail'),
]
