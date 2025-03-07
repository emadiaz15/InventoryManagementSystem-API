from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.products.models.base_model import BaseModel  # Aquí estamos usando el BaseModel común
from apps.users.models import User

class Comment(BaseModel):
    """Modelo de comentario con soporte para comentarios genéricos, creado a partir del BaseModel."""

    # Relación genérica para asociar el comentario a cualquier objeto (como Product o Subproduct)
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

    class Meta:
        ordering = ['-created_at']  # Ordena los comentarios por fecha de creación descendente

    def __str__(self):
        return f'Comment by {self.user.username if self.user else "Unknown"} on {self.content_object}'

    def delete(self, *args, **kwargs):
        """
        Soft delete: establece `status` a False y marca `deleted_at`.
        Se hereda la lógica del método `delete` del BaseModel.
        """
        user = kwargs.pop("user", None)  # Extraemos el usuario de los kwargs

        # Importación diferida para evitar la importación circular con Subproduct
        from apps.products.models.subproduct_model import Subproduct

        super().delete(*args, **kwargs)  # Llamamos al `delete` de `BaseModel` para hacer soft delete
        self.status = False
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save(update_fields=['status', 'deleted_at', 'deleted_by'])

    def restore(self):
        """
        Restaura un comentario eliminado, estableciendo `deleted_at` a None y `status` a True.
        """
        self.deleted_at = None
        self.status = True
        self.deleted_by = None
        self.save(update_fields=['deleted_at', 'status', 'deleted_by'])
