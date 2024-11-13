from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
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
        # Validación de campos esenciales
        if not data.get('text'):
            raise serializers.ValidationError("El comentario no puede estar vacío.")
        
        # Validación de `content_type` y `object_id`
        content_type = data.get('content_type').lower()
        object_id = data.get('object_id')
        
        # Verificar que el modelo referenciado exista
        try:
            model = ContentType.objects.get(model=content_type).model_class()
            if not model.objects.filter(id=object_id).exists():
                raise serializers.ValidationError("El objeto de referencia no existe.")
        except ContentType.DoesNotExist:
            raise serializers.ValidationError("Tipo de contenido no válido.")
        
        return data

    def create(self, validated_data):
        # Extrae y elimina los campos `content_type` y `object_id` de los datos validados
        content_type = validated_data.pop('content_type').lower()
        object_id = validated_data.pop('object_id')
        
        # Obtiene la instancia de ContentType y crea el comentario genérico
        content_type_instance = ContentType.objects.get(model=content_type)
        comment = Comment.objects.create(
            content_type=content_type_instance,
            object_id=object_id,
            **validated_data
        )
        return comment

    def soft_delete(self):
        # Llamada al método delete del modelo para realizar la eliminación suave
        self.instance.delete(soft=True)

    def restore(self):
        # Restaurar el comentario
        self.instance.deleted_at = None
        self.instance.save(update_fields=['deleted_at'])
