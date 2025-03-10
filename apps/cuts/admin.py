from django.contrib import admin
from apps.cuts.models.cutting_order_model import CuttingOrder

@admin.register(CuttingOrder)
class CuttingOrderAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo CuttingOrder.
    """
    list_display = (
        'id', 'customer', 'subproduct', 'cutting_quantity', 'status', 
        'created_at', 'assigned_by', 'assigned_to'
    )
    search_fields = ('customer', 'subproduct__name', 'assigned_by__username', 'assigned_to__username')
    
    # Removido 'updated_at' si no existe o no es un filtro válido
    list_filter = ('status', 'created_at')  # No usamos 'updated_at', sino 'modified_at'
    
    ordering = ('-created_at',)
    
    # Usamos 'modified_at' en lugar de 'updated_at'
    readonly_fields = ('created_at', 'modified_at', 'completed_at')
    
    # Agregado 'modified_at' en lugar de 'updated_at' para que se muestre en la interfaz de administración
    fieldsets = (
        (None, {
            'fields': ('customer', 'subproduct', 'cutting_quantity', 'status', 'assigned_by', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at', 'completed_at', 'deleted_at'),
        }),
    )
