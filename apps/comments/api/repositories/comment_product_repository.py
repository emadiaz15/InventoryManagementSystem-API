from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone

from apps.comments.models import ProductComment

class ProductCommentRepository:
    """Repositorio para manejar comentarios sobre productos."""

    @staticmethod
    def create_comment(product, user, text):
        """Crea un nuevo comentario asociado a un producto."""
        with transaction.atomic():
            comment = ProductComment.objects.create(
                product=product,
                text=text,
                created_by=user,  # Usamos 'created_by' en lugar de 'user'
                modified_by=None,  # 'modified_by' es None al principio
            )
            return comment

    @staticmethod
    def get_comments(product_id):
        """Obtiene los comentarios activos de un producto específico."""
        return ProductComment.objects.filter(product_id=product_id, status=True)  # Filtrar por estado activo

    @staticmethod
    def get_comment_by_id(comment_id):
        """Obtiene un comentario específico por su ID."""
        try:
            return ProductComment.objects.get(id=comment_id, status=True)
        except ProductComment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comentario con id {comment_id} no existe.")

    @staticmethod
    def update_comment(comment_id, text, user):
        """Actualiza un comentario de producto."""
        try:
            comment = ProductComment.objects.get(id=comment_id)
            comment.text = text
            comment.modified_by = user
            comment.modified_at = timezone.now()
            comment.save()
            return comment
        except ProductComment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comentario con id {comment_id} no existe.")

    @staticmethod
    def soft_delete_comment(comment_id, user):
        """Realiza un soft delete de un comentario de producto."""
        try:
            comment = ProductComment.objects.get(id=comment_id)
            comment.delete(user=user)  # Usa el método delete con el usuario
            return comment
        except ProductComment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comentario con id {comment_id} no existe.")

    @staticmethod
    def restore_comment(comment_id):
        """Restaura un comentario de producto previamente eliminado."""
        try:
            comment = ProductComment.objects.get(id=comment_id)
            comment.restore()
            return comment
        except ProductComment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comentario con id {comment_id} no existe.")
