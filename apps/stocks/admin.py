from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ProductStock, SubproductStock, StockEvent

@admin.register(StockEvent)
class StockEventAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'get_stock',
        'stock_quantity',
        'quantity_change',
        'event_type',
        'created_at',
        'created_by', 
        'modified_at',
        'modified_by'
    ]
    search_fields = ['stock__id', 'created_by__username']  # Use created_by__username
    list_filter = ['event_type', 'created_at', 'created_by']  # Use created_by
    ordering = ['-created_at']
    readonly_fields = ['stock_details']

    def get_stock(self, obj):
        """Devuelve el ID del stock asociado."""
        return obj.stock.id if obj.stock else None
    get_stock.short_description = _('Stock ID')

    def stock_quantity(self, obj):
        """Devuelve la cantidad actual del stock relacionado con el evento."""
        return obj.stock.quantity if obj.stock else "No stock"
    stock_quantity.short_description = _('Stock Quantity')

    def modified_at(self, obj):
        """Devuelve la fecha de modificación del evento."""
        return obj.modified_at
    modified_at.short_description = _('Modified At')

    def modified_by(self, obj):
        """Devuelve el usuario que modificó el evento."""
        return obj.modified_by
    modified_by.short_description = _('Modified By')

    def stock_details(self, obj):
        """Devuelve un resumen del stock en la vista de detalle."""
        if obj.stock:
            return f"Stock {obj.stock.id} - {obj.stock.quantity} unidades"
        return "No stock"
    stock_details.short_description = _('Stock Details')
