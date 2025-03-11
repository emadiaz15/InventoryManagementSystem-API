from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone

from apps.comments.models import SubproductComment


class SubproductCommentRepository:
    """Repositorio para manejar comentarios sobre subproductos."""

    @staticmethod
    def create_comment(subproduct, user, text):
        """Crea un nuevo comentario asociado a un subproducto."""
        with transaction.atomic():
            # Usamos 'created_by' en lugar de 'user'
            comment = SubproductComment.objects.create(
                subproduct=subproduct,
                text=text,
                created_by=user,  # Asociamos al usuario con 'created_by'
                modified_by=None,  # 'modified_by' es None al principio
                modified_at=None,
                deleted_at=None,
                deleted_by=None,
                status=True  # El comentario está activo por defecto
            )
            return comment

    @staticmethod
    def get_comments(subproduct_id):
        """Obtiene los comentarios activos de un subproducto específico."""
        return SubproductComment.active_objects.filter(subproduct_id=subproduct_id)

    @staticmethod
    def get_comment_by_id(comment_id):
        """Obtiene un comentario específico por su ID."""
        try:
            return SubproductComment.objects.get(id=comment_id)
        except SubproductComment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comentario con id {comment_id} no existe.")

    @staticmethod
    def update_comment(comment_id, text, user):
        """Actualiza un comentario de subproducto."""
        try:
            comment = SubproductComment.objects.get(id=comment_id, status=True)
            # Solo actualizamos si el texto cambia, para evitar una actualización innecesaria
            if comment.text != text:
                comment.text = text
                comment.modified_by = user
                comment.modified_at = timezone.now()  # Actualizamos la fecha de modificación
                comment.save()
            return comment
        except SubproductComment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comentario con id {comment_id} no existe.")

    @staticmethod
    def soft_delete_comment(comment_id, user):
        """Realiza un soft delete de un comentario de subproducto."""
        try:
            comment = SubproductComment.objects.get(id=comment_id)
            comment.delete(user=user)  # Usa el método delete con el usuario
            return comment
        except SubproductComment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comentario con id {comment_id} no existe.")

    @staticmethod
    def restore_comment(comment_id):
        """Restaura un comentario de subproducto previamente eliminado."""
        try:
            comment = SubproductComment.objects.get(id=comment_id)
            comment.restore()
            return comment
        except SubproductComment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comentario con id {comment_id} no existe.")
