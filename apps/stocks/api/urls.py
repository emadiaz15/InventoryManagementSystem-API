from django.urls import path
from apps.stocks.api.views.stock_event_view import stock_event_history

urlpatterns = [
    # Rutas para ver el historial de eventos de stock
    path('products/<int:pk>/stock/events/', stock_event_history, {'entity_type': 'product'}, name='product-stock-events'),
    path('products/<int:product_pk>/subproducts/<int:pk>/stock/events/', stock_event_history, {'entity_type': 'subproduct'}, name='subproduct-stock-events'),
    path('history/', stock_event_history, name='stock-event-history'),
]
