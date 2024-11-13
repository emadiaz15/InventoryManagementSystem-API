from django.contrib import admin
from apps.cuts.models import CuttingOrder

@admin.register(CuttingOrder)
class CuttingOrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'cutting_quantity', 'status', 'created_at', 'assigned_by', 'operator')
    search_fields = ('customer', 'product__name')
    list_filter = ('status', 'created_at')
