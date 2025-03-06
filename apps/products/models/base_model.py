from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseModel(models.Model):
    """Modelo base con lógica común para creación, modificación y eliminación soft."""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Se asigna automáticamente al crear
    modified_at = models.DateTimeField(null=True, blank=True)  # Inicialmente null
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="%(class)s_created",
        null=True, blank=True
    )
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="%(class)s_modified",
        null=True, blank=True
    )
    deleted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="%(class)s_deleted",
        null=True, blank=True
    )

    status = models.BooleanField(default=True)

    class Meta:
        abstract = True  # No se crea una tabla para este modelo directamente


    def save(self, *args, **kwargs):
        """Lógica para asignar 'created_by', 'modified_by', y 'modified_at'"""
        user = kwargs.pop("user", None)  # Extraemos el 'user' de kwargs si está presente.
        
        if not self.pk and user:  # Si es un objeto nuevo
            self.created_by = user
            self.modified_by = None  # Aseguramos que 'modified_by' es None al crear.
            self.modified_at = None  # Aseguramos que 'modified_at' es None al crear.
        elif user:  # Si hay un usuario y es una modificación
            self.modified_by = user
            if not self.modified_at:
                self.modified_at = timezone.now()  # Asignamos 'modified_at' solo si no existe

        super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        """Realiza un soft delete (cambia el status a False y marca deleted_at)."""
        user = kwargs.pop("user", None)
        self.status = False
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save(update_fields=['status', 'deleted_at', 'deleted_by'])
