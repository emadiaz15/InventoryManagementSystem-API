from django.urls import path
from apps.stocks.api.views.stock_event_product_view import product_stock_event_history
from apps.stocks.api.views.stock_event_subproduct_view import subproduct_stock_event_history

urlpatterns = [
    # Historial de eventos de stock para productos
    path('products/<int:product_pk>/stock/events/', product_stock_event_history, name='product-stock-events'),

    # Historial de eventos de stock para subproductos
    path('products/<int:product_pk>/subproducts/<int:subproduct_pk>/stock/events/', subproduct_stock_event_history, name='subproduct-stock-events'),
]