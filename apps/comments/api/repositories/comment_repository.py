from apps.comments.models.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

class CommentRepository:
    """Repositorio para manejar operaciones sobre los comentarios."""

    @staticmethod
    def create_comment(content_type_str, object_id, user, text):
        """
        Crea un comentario y lo asigna a un modelo genérico (Product, Subproduct, etc.)
        """
        try:
            # Verificar si el ContentType existe
            content_type = ContentType.objects.get(model=content_type_str.lower())
            
            # Crear comentario
            comment = Comment.objects.create(
                content_type=content_type,
                object_id=object_id,
                user=user,
                text=text
            )
            return comment

        except ContentType.DoesNotExist:
            raise ValueError(f"Content type '{content_type_str}' does not exist.")
    
    @staticmethod
    def get_comments(content_type_str, object_id):
        """
        Obtiene los comentarios asociados a un objeto basado en su content_type y object_id.
        """
        try:
            # Obtiene el ContentType
            content_type = ContentType.objects.get(model=content_type_str.lower())

            # Filtra comentarios activos
            comments = Comment.active_objects.filter(content_type=content_type, object_id=object_id)
            return comments

        except ContentType.DoesNotExist:
            raise ValueError(f"Content type '{content_type_str}' does not exist.")
    
    @staticmethod
    def get_comment_by_id(comment_id):
        """
        Obtiene un comentario específico por su ID.
        """
        try:
            return Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comment with id {comment_id} does not exist.")
    
    @staticmethod
    def soft_delete_comment(comment_id, user):
        """
        Realiza un soft delete del comentario dado su ID.
        """
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.delete(user=user)  # Usa el método delete con el usuario
            return comment
        except Comment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comment with id {comment_id} does not exist.")
    
    @staticmethod
    def restore_comment(comment_id):
        """
        Restaura un comentario previamente eliminado.
        """
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.restore()  # Usa el método restore del modelo
            return comment
        except Comment.DoesNotExist:
            raise ObjectDoesNotExist(f"Comment with id {comment_id} does not exist.")
