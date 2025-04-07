from django.contrib import admin
from .models.user_model import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'name', 'last_name')
    list_filter = ('is_staff', 'is_active')
    list_editable = ('is_staff', 'is_active')  # Hacer que los campos is_staff e is_active sean editables en línea

    def activate_users(self, request, queryset):
        """
        Acción personalizada para activar usuarios seleccionados.
        """
        queryset.update(is_active=True)

    def deactivate_users(self, request, queryset):
        """
        Acción personalizada para desactivar usuarios seleccionados.
        """
        queryset.update(is_active=False)

    # Registrar las acciones personalizadas
    actions = ['activate_users', 'deactivate_users']

    activate_users.short_description = "Activar usuarios seleccionados"
    deactivate_users.short_description = "Desactivar usuarios seleccionados"

admin.site.register(User, UserAdmin)
