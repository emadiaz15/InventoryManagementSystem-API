from rest_framework import serializers
from django.utils import timezone
from apps.users.models import User

class BaseCommentSerializer(serializers.ModelSerializer):
    """Clase base para comentarios de productos y subproductos, evitando código repetitivo."""

    user = serializers.StringRelatedField(read_only=True)  # Usuario que hizo el comentario

    class Meta:
        fields = ['id', 'user', 'text', 'created_at', 'modified_at', 'deleted_at', 'deleted_by', 'status']
        read_only_fields = ['id', 'created_at', 'modified_at', 'deleted_at', 'deleted_by', 'status']

    def validate_text(self, value):
        """Evita comentarios vacíos."""
        if not value.strip():
            raise serializers.ValidationError("El comentario no puede estar vacío.")
        return value    
    
    def soft_delete(self):
        """Soft delete del comentario."""
        if not getattr(self, 'instance', None):
            raise serializers.ValidationError("No hay comentario para eliminar.")
        self.instance.status = False
        self.instance.deleted_at = timezone.now()
        self.instance.save(update_fields=['status', 'deleted_at'])

    def restore(self):
        """Restaura un comentario eliminado."""
        if not getattr(self, 'instance', None):
            raise serializers.ValidationError("No hay comentario para restaurar.")
        self.instance.status = True
        self.instance.deleted_at = None
        self.instance.save(update_fields=['status', 'deleted_at'])

    def create(self, validated_data):
        """Sobreescribe el método create para agregar 'created_by', 'modified_by'."""
        user = self.context['request'].user  # Obtener el usuario autenticado
        validated_data['created_by'] = user
        validated_data['modified_by'] = None  # Inicialmente, 'modified_by' es None
        validated_data['created_at'] = timezone.now()
        validated_data['modified_at'] = None
        validated_data['deleted_at'] = None
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Sobreescribe el método update para actualizar 'modified_by' y 'modified_at'."""
        request = self.context.get('request', None)
        user = request.user if request and hasattr(request, "user") else None

        if user:
            if any(field in validated_data for field in ['text', 'status']):
                validated_data['modified_by'] = user
                validated_data['modified_at'] = timezone.now()

        if 'status' in validated_data and validated_data['status'] is False:
            validated_data['deleted_by'] = user
            validated_data['deleted_at'] = timezone.now()

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Ajusta la representación del objeto para asegurar valores correctos."""
        data = super().to_representation(instance)

        # Ajustamos el campo 'modified_by' y 'deleted_by' para evitar valores nulos innecesarios
        if instance.modified_by is None:
            data['modified_by'] = None

        if not instance.deleted_by and instance.status != False:
            data['deleted_by'] = None

        # Aseguramos que 'created_by' esté presente
        if instance.created_by:
            data['created_by'] = instance.created_by.username  # O el campo que prefieras mostrar

        return data
