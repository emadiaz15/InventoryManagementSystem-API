from django.contrib import admin
from django.utils.safestring import mark_safe
from apps.products.models import Category, Type, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Category.
    """
    list_display = ('name', 'status', 'created_at', 'deleted_at', 'user')  # Columnas a mostrar
    list_filter = ('status', 'deleted_at')  # Filtros laterales
    search_fields = ('name', 'description')  # Campos para búsqueda
    ordering = ('name',)  # Orden alfabético


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Type.
    """
    list_display = ('name', 'status', 'category', 'created_at', 'deleted_at', 'user')  # Añadido `category` para más contexto
    list_filter = ('status', 'category', 'deleted_at')  # Filtros por categoría y estado
    search_fields = ('name', 'description')  # Campos para búsqueda
    ordering = ('name',)  # Orden alfabético


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Product.
    """
    list_display = ('name', 'code', 'category', 'type', 'created_at', 'deleted_at', 'user', 'technical_sheet_photo_display')
    list_filter = ('category', 'type', 'deleted_at')  # Filtros por categoría, tipo y estado
    search_fields = ('name', 'code', 'description')  # Campos para búsqueda
    ordering = ('name',)  # Orden alfabético
    raw_id_fields = ('category', 'type')  # Uso de selectores compactos para relaciones ForeignKey

    def technical_sheet_photo_display(self, obj):
        """
        Muestra la imagen de la ficha técnica en el panel de administración.
        """
        if obj.technical_sheet_photo:  # Verifica si el campo `technical_sheet_photo` tiene datos
            return mark_safe(f'<img src="{obj.technical_sheet_photo.url}" width="100" height="100" />')
        return "No Image"
    technical_sheet_photo_display.short_description = 'Ficha Técnica'
