from django.contrib import admin
from apps.cuts.models.cutting_order_model import CuttingOrder, CuttingOrderItem

class CuttingOrderItemInline(admin.TabularInline):
    model = CuttingOrderItem
    extra = 0
    readonly_fields = ('subproduct', 'cutting_quantity')
    verbose_name = "Item de Orden de Corte"
    verbose_name_plural = "Items de Orden de Corte"

@admin.register(CuttingOrder)
class CuttingOrderAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo CuttingOrder,
    con inline de sus items y usando created_by en lugar de assigned_by.
    """
    list_display = (
        'id',
        'customer',
        'item_count',
        'status',
        'created_at',
        'created_by',
        'assigned_to',
        'workflow_status',
    )
    search_fields = (
        'customer',
        'items__subproduct__brand',
        'created_by__username',
        'assigned_to__username',
    )
    list_filter = ('status', 'workflow_status', 'created_at')
    ordering = ('-created_at',)

    readonly_fields = (
        'created_at',
        'modified_at',
        'completed_at',
        'deleted_at',
        'created_by',
        'modified_by',
        'deleted_by',
    )

    fieldsets = (
        (None, {
            'fields': (
                'customer',
                'workflow_status',
                'assigned_to',
            )
        }),
        ('Timestamps & Audit', {
            'fields': (
                'created_at',
                'modified_at',
                'completed_at',
                'deleted_at',
                'created_by',
                'modified_by',
                'deleted_by',
            )
        }),
    )

    inlines = [CuttingOrderItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Número de Ítems'
