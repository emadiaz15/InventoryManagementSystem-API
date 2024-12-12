from django.utils.timezone import now
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class ActiveCommentManager(models.Manager):
    def get_queryset(self):
        # Solo devuelve los comentarios no eliminados
        return super().get_queryset().filter(deleted_at__isnull=True)

class Comment(models.Model):
    # Relación genérica para permitir comentarios en cualquier modelo, por ejemplo Product
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="comments",
        default=1  # Valor por defecto temporal, asegurarse de que ContentType id=1 exista
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='comments', null=True)
    text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Campo para soft delete

    # Managers
    objects = models.Manager()  # Manager por defecto
    active_objects = ActiveCommentManager()  # Manager para comentarios activos

    def __str__(self):
        # Mensaje en inglés para mantener consistencia
        return f'Comment by {self.user.username if self.user else "Unknown"} on {self.content_object}'

    def delete(self, *args, **kwargs):
        """
        Soft delete: establece `deleted_at` en la fecha y hora actuales en lugar de eliminar el registro.
        """
        self.deleted_at = now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        """
        Restaura un comentario eliminado, estableciendo `deleted_at` a None.
        """
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    class Meta:
        ordering = ['-created_at']  # Ordena por fecha de creación descendente
