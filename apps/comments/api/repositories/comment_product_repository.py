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
                modified_at=None,
                deleted_at=None,
                deleted_by=None,
                status=True  # Inicialmente, el comentario está activo
            )
            return comment

    @staticmethod
    def get_comments(product_id):
        """Obtiene los comentarios activos de un producto específico."""
        return ProductComment.objects.filter(product_id=product_id, status=True)  # Filtrar por estado activo

    @staticmethod
    def get_comment_by_id(comment_id):
        """Obtiene un comentario específico por su ID y estado activo."""
        try:
            return ProductComment.objects.get(id=comment_id, status=True)
        except ProductComment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comentario con id {comment_id} no existe o está eliminado.")

    @staticmethod
    def update_comment(comment_id, text, user):
        """Actualiza un comentario de producto."""
        try:
            comment = ProductComment.objects.get(id=comment_id, status=True)
            # Solo actualizamos si el texto cambia, para evitar una actualización innecesaria
            if comment.text != text:
                comment.text = text
                comment.modified_by = user
                comment.modified_at = timezone.now()  # Actualizamos la fecha de modificación
                comment.save()
            return comment
        except ProductComment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comentario con id {comment_id} no existe o está eliminado.")

    @staticmethod
    def soft_delete_comment(comment_id, user):
        """Realiza un soft delete de un comentario de producto."""
        try:
            comment = ProductComment.objects.get(id=comment_id, status=True)  # Aseguramos que el comentario esté activo
            comment.status = False  # Marcamos el estado como eliminado
            comment.deleted_at = timezone.now()  # Asignamos la fecha de eliminación
            comment.deleted_by = user  # Guardamos quién realizó la eliminación
            comment.save(update_fields=['status', 'deleted_at', 'deleted_by'])  # Solo actualizamos los campos relevantes
            return comment
        except ProductComment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comentario con id {comment_id} no existe o ya está eliminado.")

    @staticmethod
    def restore_comment(comment_id):
        """Restaura un comentario de producto previamente eliminado."""
        try:
            comment = ProductComment.objects.get(id=comment_id, status=False)  # Aseguramos que el comentario esté eliminado
            comment.status = True  # Restauramos el estado
            comment.deleted_at = None  # Limpiamos la fecha de eliminación
            comment.deleted_by = None  # Limpiamos el usuario que eliminó el comentario
            comment.save(update_fields=['status', 'deleted_at', 'deleted_by'])  # Solo actualizamos estos campos
            return comment
        except ProductComment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comentario con id {comment_id} no existe o no está eliminado.")
