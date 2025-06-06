from django.contrib import admin
from .models import Category, Type, Product, Subproduct

# Admin para categorías
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'name', 'status', 'created_by']
    search_fields = ['name']
    list_filter = ['status']
    ordering = ['name']

# Admin para tipos
@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'name', 'status', 'created_by']
    search_fields = ['name']
    list_filter = ['status', 'category']
    ordering = ['category', 'name']

# Admin genérico para productos
class GenericProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'category', 'type', 'status', 'created_by', 'modified_at']
    search_fields = ['name', 'code']
    list_filter = ['status', 'category', 'type']
    ordering = ['name', 'code']

    readonly_fields = ['total_stock']

    def total_stock(self, obj):
        """Devuelve el stock total (producto + subproductos)."""
        return obj.total_stock
    total_stock.short_description = 'Total Stock'

# Herencia para extender el comportamiento de ProductAdmin sin registrarlo de nuevo
@admin.register(Product)
class ProductAdmin(GenericProductAdmin):
    pass

# Admin para subproductos
@admin.register(Subproduct)
class SubproductAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand', 'parent', 'status', 'total_stock', 'created_at']
    search_fields = ['brand', 'parent__name']
    list_filter = ['status', 'parent__category']
    ordering = ['brand', 'parent']

    def total_stock(self, obj):
        """Devuelve el stock total del subproducto."""
        return obj.total_stock
    total_stock.short_description = 'Total Stock'
