from django.contrib import admin
from apps.stocks.models import Stock, StockHistory


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Stock.
    """
    list_display = ('id', 'product', 'subproduct', 'quantity', 'created_at', 'updated_at', 'user')  # Columnas a mostrar
    list_filter = ('product', 'subproduct', 'created_at', 'updated_at', 'user')  # Filtros laterales
    search_fields = ('product__name', 'subproduct__name', 'user__username')  # Campos para búsqueda
    ordering = ('-created_at',)  # Orden descendente por fecha de creación
    readonly_fields = ('created_at', 'updated_at')  # Evitar la edición de las marcas de tiempo

    fieldsets = (
        (None, {
            'fields': ('product', 'subproduct', 'quantity', 'user')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def view_stock_history(self, obj):
        """
        Muestra un resumen del historial relacionado con el registro de stock.
        """
        return ", ".join(
            [f"{history.change_reason} ({history.recorded_at})" for history in obj.product.stock_history.all()]
        )

    view_stock_history.short_description = 'Historial de Cambios'
    list_display += ('view_stock_history',)


@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo StockHistory.
    """
    list_display = ('id', 'product', 'subproduct', 'stock_before', 'stock_after', 'change_reason', 'recorded_at', 'user')  # Columnas a mostrar
    list_filter = ('product', 'subproduct', 'recorded_at', 'user')  # Filtros laterales
    search_fields = ('product__name', 'subproduct__name', 'change_reason', 'user__username')  # Campos para búsqueda
    ordering = ('-recorded_at',)  # Orden descendente por fecha de registro

    readonly_fields = ('recorded_at',)  # Evitar la edición directa del campo de fecha
    fieldsets = (
        (None, {
            'fields': ('product', 'subproduct', 'stock_before', 'stock_after', 'change_reason', 'user')
        }),
        ('Timestamps', {
            'fields': ('recorded_at',),
        }),
    )
