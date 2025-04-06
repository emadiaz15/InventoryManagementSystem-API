from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseModel(models.Model):
    """
    Modelo base con lógica común para creación, modificación, eliminación soft
    y ordenamiento por defecto (más recientes primero).
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    modified_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Modificación")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Eliminación")

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="%(app_label)s_%(class)s_created",
        null=True, blank=True, verbose_name="Creado por"
    )
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="%(app_label)s_%(class)s_modified",
        null=True, blank=True, verbose_name="Modificado por"
    )
    deleted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="%(app_label)s_%(class)s_deleted",
        null=True, blank=True, verbose_name="Eliminado por"
    )

    status = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """
        Lógica simplificada para asignar 'created_by', 'modified_by', y 'modified_at'.
        Llama a super().save() una sola vez al final.
        """
        # Extrae 'user' si se pasó, SIN eliminarlo aún si super().save necesita todos los kwargs
        user = kwargs.get("user", None)
        # Eliminar 'user' de kwargs SOLO si super().save() NO lo espera (lo cual es lo normal)
        if "user" in kwargs:
             kwargs.pop("user")

        is_new = self.pk is None

        # Asignar campos de auditoría ANTES de llamar a super().save()
        if is_new and user:
            self.created_by = user
        elif not is_new: # Es una actualización
            self.modified_at = timezone.now()
            if user:
                self.modified_by = user

        # Llamar al método save original UNA VEZ para persistir todos los cambios
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Realiza un soft delete (cambia el status a False y marca deleted_at/by)."""
        user = kwargs.pop("user", None) # Extrae user si se pasó
        self.status = False
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        # Llama a super().save() para evitar recursión y guardar solo estos campos
        # No pasamos 'user' aquí porque ya asignamos deleted_by.
        super().save(update_fields=['status', 'deleted_at', 'deleted_by'], *args, **kwargs)
