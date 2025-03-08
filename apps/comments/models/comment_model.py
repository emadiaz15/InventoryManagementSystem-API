from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.users.models import User
from apps.products.models.base_model import BaseModel

class ActiveCommentManager(models.Manager):
    """Manager para obtener solo los comentarios activos (status=True)."""
    def get_queryset(self):
        return super().get_queryset().filter(status=True)

class Comment(BaseModel):
    """Modelo de comentario que puede asociarse a productos y subproductos."""
    
    # Relación genérica para asociar el comentario a cualquier objeto (Product, Subproduct)
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE, 
        related_name="comments", 
        default=1  # Valor temporal, asegurarse que ContentType id=1 exista
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='comments', null=True)
    text = models.TextField(null=True, blank=True)
    
    # Agregar el manager personalizado
    active_objects = ActiveCommentManager()

    status = models.BooleanField(default=True)  # Estado del comentario (activo o no)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Fecha de eliminación
    deleted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='deleted_comments', 
        null=True, 
        blank=True
    )  # Usuario que eliminó el comentario
    
    class Meta:
        ordering = ['-created_at']  # Ordena los comentarios por fecha de creación descendente

    def __str__(self):
        return f'Comentario por {self.user.username if self.user else "Desconocido"} sobre {self.content_object}'

    def delete(self, *args, **kwargs):
        """
        Soft delete: establece `status` a False y marca `deleted_at`.
        """
        user = kwargs.pop("user", None)  # Extraemos el usuario de los kwargs

        # Marcar como eliminado
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
