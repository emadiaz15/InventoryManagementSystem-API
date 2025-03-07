from django.contrib import admin
from apps.comments.models.models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_related_object', 'user', 'text', 'created_at', 'deleted_at')
    list_filter = ('deleted_at', 'created_at')
    search_fields = ('text', 'user__username', 'content_type__model')
    readonly_fields = ('created_at', 'modified_at')

    def get_related_object(self, obj):
        # Devuelve el nombre del objeto relacionado (Product o SubProduct)
        return obj.content_object  # Usa content_object para obtener el objeto relacionado

    get_related_object.short_description = 'Related Object'
