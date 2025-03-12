from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseModel(models.Model):
    """Modelo base con lógica común para creación, modificación y eliminación soft."""
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="%(class)s_created", null=True, blank=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="%(class)s_modified", null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="%(class)s_deleted", null=True, blank=True)
    status = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Lógica para asignar 'created_by', 'modified_by', y 'modified_at'."""
        user = kwargs.pop("user", None)

        if not self.pk and user:
            self.created_by = user
            self.modified_by = None
            self.modified_at = None

        elif self.pk:
            if user:
                self.modified_by = user
            if not self.modified_at:
                self.modified_at = timezone.now()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Realiza un soft delete (cambia el status a False y marca deleted_at)."""
        user = kwargs.pop("user", None)
        self.status = False
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        super().save(update_fields=['status', 'deleted_at', 'deleted_by'])
