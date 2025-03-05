from django.contrib import admin
from django.utils.safestring import mark_safe
from apps.products.models import Category, Type, Product  # 🔥 Corregimos la importación

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Category.
    """
    list_display = ('name', 'status', 'created_at', 'deleted_at', 'created_by')  # 🔥 Reemplazamos 'user' por 'created_by'
    list_filter = ('status', 'deleted_at')  
    search_fields = ('name', 'description')  
    ordering = ('name',)  

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Type.
    """
    list_display = ('name', 'status', 'category', 'created_at', 'deleted_at', 'created_by')  # 🔥 Reemplazamos 'user' por 'created_by'
    list_filter = ('status', 'category', 'deleted_at')  
    search_fields = ('name', 'description')  
    ordering = ('name',)  

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Product.
    """
    list_display = ('name', 'code', 'category', 'type', 'created_at', 'deleted_at', 'created_by', 'technical_sheet_photo_display')  # 🔥 Reemplazamos 'user' por 'created_by'
    list_filter = ('category', 'type', 'deleted_at')  
    search_fields = ('name', 'code', 'description')  
    ordering = ('name',)  
    raw_id_fields = ('category', 'type')  

    def technical_sheet_photo_display(self, obj):
        """
        Muestra la imagen de la ficha técnica en el panel de administración.
        """
        if obj.technical_sheet_photo:  
            return mark_safe(f'<img src="{obj.technical_sheet_photo.url}" width="100" height="100" />')
        return "No Image"
    
    technical_sheet_photo_display.short_description = 'Ficha Técnica'
