from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.products.models.category_model import Category
from apps.products.models.product_model import Product
from apps.products.models.type_model import Type
from apps.products.models.subproduct_model import Subproduct

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Category.
    """
    list_display = ('name', 'status', 'created_at', 'deleted_at', 'created_by')  # 🔥 Reemplazamos 'user' por 'created_by'
    list_filter = ('status', 'deleted_at')  
    search_fields = ('name', 'description')  
    ordering = ('name',)

    # Asegúrate de que 'created_at', 'deleted_at' y 'created_by' existan en el modelo.
    def created_at(self, obj):
        return obj.created_at
    created_at.admin_order_field = 'created_at'
    created_at.short_description = 'Fecha de Creación'

    def deleted_at(self, obj):
        return obj.deleted_at
    deleted_at.admin_order_field = 'deleted_at'
    deleted_at.short_description = 'Fecha de Eliminación'

    def created_by(self, obj):
        return obj.created_by.username if obj.created_by else 'N/A'
    created_by.short_description = 'Creado por'


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Type.
    """
    list_display = ('name', 'status', 'category', 'created_at', 'deleted_at', 'created_by')  # 🔥 Reemplazamos 'user' por 'created_by'
    list_filter = ('status', 'category', 'deleted_at')  
    search_fields = ('name', 'description')  
    ordering = ('name',)

    def created_at(self, obj):
        return obj.created_at
    created_at.admin_order_field = 'created_at'
    created_at.short_description = 'Fecha de Creación'

    def deleted_at(self, obj):
        return obj.deleted_at
    deleted_at.admin_order_field = 'deleted_at'
    deleted_at.short_description = 'Fecha de Eliminación'

    def created_by(self, obj):
        return obj.created_by.username if obj.created_by else 'N/A'
    created_by.short_description = 'Creado por'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Product.
    """
    list_display = ('name', 'code', 'category', 'type', 'created_at', 'deleted_at', 'created_by', 'technical_sheet_photo_display')  # 🔥 Reemplazamos 'user' por 'created_by'
    list_filter = ('category', 'type')  
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

    # Agregar los campos 'created_at', 'deleted_at' y 'created_by'
    def created_at(self, obj):
        return obj.created_at
    created_at.admin_order_field = 'created_at'
    created_at.short_description = 'Fecha de Creación'

    def deleted_at(self, obj):
        return obj.deleted_at
    deleted_at.admin_order_field = 'deleted_at'
    deleted_at.short_description = 'Fecha de Eliminación'

    def created_by(self, obj):
        return obj.created_by.username if obj.created_by else 'N/A'
    created_by.short_description = 'Creado por'
