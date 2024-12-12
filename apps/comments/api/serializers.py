# Este archivo define el serializer para manejar la creación, validación, y eliminación suave de comentarios genéricos.

from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from apps.comments.models import Comment

class CommentSerializer(serializers.ModelSerializer):
    # Campos adicionales para manejar el comentario genérico
    content_type = serializers.CharField(write_only=True)
    object_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content_type', 'object_id', 'user', 'text', 'created_at', 'modified_at', 'deleted_at']
        read_only_fields = ['id', 'created_at', 'modified_at', 'deleted_at']

    def validate(self, data):
        """
        Validación de los datos del comentario, asegurando que el contenido y el objeto de referencia existen.
        """
        # Validación de campo `text` obligatorio
        if not data.get('text'):
            # Mensaje en inglés:
            raise serializers.ValidationError("The comment cannot be empty.")

        # Validación de `content_type` y `object_id`
        content_type_str = data.get('content_type').lower()
        object_id = data.get('object_id')

        # Verificar que el modelo referenciado existe y el objeto es válido
        try:
            model_class = ContentType.objects.get(model=content_type_str).model_class()
            if not model_class.objects.filter(id=object_id).exists():
                # Mensaje en inglés:
                raise serializers.ValidationError("The referenced object does not exist.")
        except ContentType.DoesNotExist:
            # Mensaje en inglés:
            raise serializers.ValidationError("Invalid content type.")

        return data

    def create(self, validated_data):
        """
        Crea un comentario genérico asignado a un `content_type` y `object_id` específicos.
        """
        content_type_str = validated_data.pop('content_type').lower()
        object_id = validated_data.pop('object_id')

        # Obtiene la instancia de ContentType y crea el comentario genérico
        content_type_instance = ContentType.objects.get(model=content_type_str)
        comment = Comment.objects.create(
            content_type=content_type_instance,
            object_id=object_id,
            **validated_data
        )
        return comment

    def soft_delete(self):
        """
        Realiza la eliminación suave del comentario estableciendo `deleted_at`.
        """
        self.instance.delete()  # Llama al método delete del modelo (soft delete)

    def restore(self):
        """
        Restaura un comentario eliminado estableciendo `deleted_at` a None.
        """
        self.instance.restore()
