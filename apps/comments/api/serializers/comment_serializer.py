from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from apps.comments.models.comment_model import Comment
from apps.users.models import User

class CommentSerializer(serializers.ModelSerializer):
    # Campos adicionales para manejar el comentario genérico
    content_type = serializers.CharField(write_only=True)  # El tipo de contenido, ej. 'product' o 'subproduct'
    object_id = serializers.IntegerField(write_only=True)  # El ID del objeto asociado (producto o subproducto)

    
    # Campo 'user' es un ForeignKey, por lo que se serializa con un campo nested
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content_type', 'object_id', 'user', 'text', 'created_at', 'modified_at', 'deleted_at', 'deleted_by', 'status']
        read_only_fields = ['id', 'created_at', 'modified_at', 'deleted_at', 'deleted_by', 'status']

    def validate(self, data):
        """
        Validación de los datos del comentario, asegurando que el contenido y el objeto de referencia existen.
        """
        # Validación de campo `text` obligatorio
        if not data.get('text'):
            raise serializers.ValidationError("The comment cannot be empty.")

        # Validación de `content_type` y `object_id`
        content_type_str = data.get('content_type').lower()
        object_id = data.get('object_id')

        # Verificar que el modelo referenciado existe y el objeto es válido
        try:
            model_class = ContentType.objects.get(model=content_type_str).model_class()
            if not model_class.objects.filter(id=object_id).exists():
                raise serializers.ValidationError("The referenced object does not exist.")
        except ContentType.DoesNotExist:
            raise serializers.ValidationError("Invalid content type.")

        return data

    def create(self, validated_data):
        """
        Crea un comentario genérico asignado a un `content_type` y `object_id` específicos.
        """
        content_type_str = validated_data.pop('content_type').lower()
        object_id = validated_data.pop('object_id')

        # Obtiene la instancia de ContentType y crea el comentario genérico
        try:
            content_type_instance = ContentType.objects.get(model=content_type_str)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError("Invalid content type provided.")

        comment = Comment.objects.create(
            content_type=content_type_instance,
            object_id=object_id,
            **validated_data
        )
        return comment

    def soft_delete(self):
        """
        Realiza la eliminación suave del comentario estableciendo `deleted_at` y `status` a False.
        """
        if not self.instance:
            raise serializers.ValidationError("No instance of the comment to delete.")
        
        self.instance.delete()  # Llama al método delete del modelo (soft delete)

    def restore(self):
        """
        Restaura un comentario eliminado estableciendo `deleted_at` a None y `status` a True.
        """
        if not self.instance:
            raise serializers.ValidationError("No instance of the comment to restore.")
        
        self.instance.restore()
