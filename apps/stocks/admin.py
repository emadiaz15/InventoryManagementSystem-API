from django.contrib import admin
from .models import Stock, StockEvent
from django.utils.translation import gettext_lazy as _

# Registra el modelo Stock en el Admin
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['id', 'quantity', 'location', 'created_at', 'created_by', 'modified_at', 'modified_by']
    search_fields = ['location', 'created_by__username']
    list_filter = ['location', 'created_at']
    ordering = ['created_at']

    # Propiedad para mostrar eventos de stock relacionados
    def events(self, obj):
        return obj.events.count()
    events.short_description = _('Stock Events')

    # Campos de solo lectura para mostrar los eventos sin poder editar directamente
    readonly_fields = ['events']

# Registra el modelo StockEvent en el Admin
@admin.register(StockEvent)
class StockEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'stock', 'quantity_change', 'event_type', 'created_at', 'user', 'modified_at', 'modified_by']
    search_fields = ['stock__id', 'user__username']
    list_filter = ['event_type', 'created_at', 'user']
    ordering = ['created_at']

    # Propiedad para mostrar detalles adicionales sobre el evento
    def stock_details(self, obj):
        return f"Stock {obj.stock.id} - {obj.stock.quantity} unidades"
    stock_details.short_description = _('Stock Details')

    # Campos de solo lectura para evitar modificaciones en los eventos de stock
    readonly_fields = ['stock_details']

