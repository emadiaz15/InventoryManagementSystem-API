from django.contrib import admin
from apps.stocks.models import Stock, StockHistory

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Stock.
    """
    list_display = ('product', 'quantity', 'date', 'user')  # Columnas que se muestran en la lista de Stocks
    list_filter = ('product', 'date', 'user')  # Filtros laterales por producto, fecha y usuario
    search_fields = ('product__name', 'user__username')  # Campos que permiten búsqueda
    ordering = ('-date',)  # Orden por fecha descendente
    readonly_fields = ('date', 'modified_at')  # Campos que no se pueden editar directamente

    fieldsets = (
        (None, {
            'fields': ('product', 'quantity', 'user')
        }),
        ('Timestamps', {
            'fields': ('date', 'modified_at'),
        }),
    )

    # Método para mostrar el historial relacionado en el admin
    def view_stock_history(self, obj):
        return ", ".join([f"{history.change_reason} ({history.recorded_at})" for history in obj.product.stock_history.all()])

    view_stock_history.short_description = 'Historial de Cambios'

    # Añadir un enlace para ver el historial de cambios en cada registro de stock
    list_display += ('view_stock_history',)


@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo StockHistory.
    """
    list_display = ('product', 'stock_before', 'stock_after', 'change_reason', 'recorded_at', 'user')  # Columnas a mostrar
    list_filter = ('product', 'recorded_at', 'user')  # Filtros laterales
    search_fields = ('product__name', 'change_reason', 'user__username')  # Campos para búsqueda
    ordering = ('-recorded_at',)  # Orden descendente por fecha

    readonly_fields = ('recorded_at',)  # Evitar la edición directa del campo de fecha
    fieldsets = (
        (None, {
            'fields': ('product', 'stock_before', 'stock_after', 'change_reason', 'user')
        }),
        ('Timestamps', {
            'fields': ('recorded_at',),
        }),
    )

# Si no utilizas el decorador @admin.register, puedes registrar el modelo así:
# admin.site.register(Stock, StockAdmin)
# admin.site.register(StockHistory, StockHistoryAdmin)
