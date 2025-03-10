from django.contrib import admin
from django.apps import apps

ProductComment = apps.get_model('comments', 'ProductComment')
SubproductComment = apps.get_model('comments', 'SubproductComment')

@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'product','text', 'created_at', 'deleted_at')
    list_filter = ('deleted_at', 'created_at')
    search_fields = ('text', 'user__username', 'product__name')
    readonly_fields = ('created_at', 'modified_at')

    def get_related_product(self, obj):
        """Devuelve el producto relacionado con el comentario."""
        return obj.product.name if obj.product else "Sin Producto"

    get_related_product.short_description = 'Producto'


@admin.register(SubproductComment)
class SubproductCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'subproduct', 'text', 'created_at', 'deleted_at')
    list_filter = ('deleted_at', 'created_at')
    search_fields = ('text', 'user__username', 'subproduct__name')
    readonly_fields = ('created_at', 'modified_at')

    def get_related_subproduct(self, obj):
        """Devuelve el subproducto relacionado con el comentario."""
        return obj.subproduct.name if obj.subproduct else "Sin Subproducto"

    get_related_subproduct.short_description = 'Subproducto'
