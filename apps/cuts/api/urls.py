from django.urls import path
from apps.cuts.api.views.cutting_view import (
    cutting_order_list,
    cutting_order_assigned_list,
    cutting_order_create,
    cutting_order_detail,
)

urlpatterns = [
    # Lista todas las órdenes de corte activas (GET /cutting-orders/)
    path('cutting-orders/', cutting_order_list, name='cutting_orders_list'),

    # Lista solo las órdenes asignadas al usuario autenticado (GET /cutting-orders/assigned/)
    path('cutting-orders/assigned/', cutting_order_assigned_list, name='cutting_orders_assigned'),

    # Crea una nueva orden de corte (POST /cutting-orders/create/)
    path('cutting-orders/create/', cutting_order_create, name='cutting_order_create'),

    # Detalle, actualización y soft‑delete de una orden específica
    # (GET, PUT, PATCH, DELETE /cutting-orders/<cuts_pk>/)
    path('cutting-orders/<int:cuts_pk>/', cutting_order_detail, name='cutting_order_detail'),
]
