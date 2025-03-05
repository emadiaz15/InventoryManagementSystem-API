from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseModel(models.Model):
    """✅ Modelo base para categorías, tipos y productos con lógica común"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
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
        abstract = True  # 🚀 Hace que este modelo NO se cree en la BD

    def save(self, *args, **kwargs):
        """✅ Almacena el usuario que crea o modifica el registro"""
        user = kwargs.pop("user", None)  # Extrae el usuario de los kwargs
        if not self.pk and user:  # Si es un nuevo objeto
            self.created_by = user
        if user:  # Para modificaciones
            self.modified_by = user
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """✅ Soft delete registrando quién elimina el objeto"""
        user = kwargs.pop("user", None)
        self.status = False
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save(update_fields=['status', 'deleted_at', 'deleted_by'])
