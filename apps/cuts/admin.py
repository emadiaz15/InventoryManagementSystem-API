from django.contrib import admin
from apps.cuts.models import CuttingOrder


@admin.register(CuttingOrder)
class CuttingOrderAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo CuttingOrder.
    """
    list_display = ('id', 'customer', 'subproduct', 'cutting_quantity', 'status', 'created_at', 'assigned_by', 'assigned_to')
    search_fields = ('customer', 'subproduct__name', 'assigned_by__username', 'assigned_to__username')
    list_filter = ('status', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'completed_at')

    fieldsets = (
        (None, {
            'fields': ('customer', 'subproduct', 'cutting_quantity', 'status', 'assigned_by', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at', 'deleted_at'),
        }),
    )
