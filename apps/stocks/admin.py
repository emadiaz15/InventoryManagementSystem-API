from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ProductStock, SubproductStock, StockEvent

# Admin para ProductStock
@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ['id', 'quantity', 'location', 'total_stock_events', 'created_at', 'created_by', 'modified_at', 'modified_by']
    search_fields = ['location', 'created_by__username']
    list_filter = ['location', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['total_stock_events']

    def total_stock_events(self, obj):
        """Devuelve la cantidad de eventos de stock relacionados con este stock de producto."""
        return obj.events.count()
    total_stock_events.short_description = _('Total Stock Events')


# Admin para SubproductStock
@admin.register(SubproductStock)
class SubproductStockAdmin(admin.ModelAdmin):
    list_display = ['id', 'quantity', 'location', 'total_stock_events', 'created_at', 'created_by', 'modified_at', 'modified_by']
    search_fields = ['location', 'created_by__username']
    list_filter = ['location', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['total_stock_events']

    def total_stock_events(self, obj):
        """Devuelve la cantidad de eventos de stock relacionados con este stock de subproducto."""
        return obj.events.count()
    total_stock_events.short_description = _('Total Stock Events')

@admin.register(StockEvent)
class StockEventAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'get_stock',         # Método que devuelve el ID del stock
        'stock_quantity',
        'quantity_change',
        'event_type',
        'created_at',
        'user',
        'get_modified_at',   # Método para mostrar modified_at
        'get_modified_by'    # Método para mostrar modified_by
    ]
    search_fields = ['stock__id', 'user__username']
    list_filter = ['event_type', 'created_at', 'user']
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

    def get_modified_at(self, obj):
        """Devuelve la fecha de modificación del evento."""
        return obj.modified_at
    get_modified_at.short_description = _('Modified At')

    def get_modified_by(self, obj):
        """Devuelve el usuario que modificó el evento."""
        return obj.modified_by
    get_modified_by.short_description = _('Modified By')

    def stock_details(self, obj):
        """Devuelve un resumen del stock en la vista de detalle."""
        if obj.stock:
            return f"Stock {obj.stock.id} - {obj.stock.quantity} unidades"
        return "No stock"
    stock_details.short_description = _('Stock Details')
