from rest_framework import serializers
from apps.products.models import Category, Type
from .base_serializer import BaseSerializer  # 🚀 Importamos la clase base

class TypeSerializer(BaseSerializer):
    # Relación con la categoría, un campo de clave primaria
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)

    # Campos relacionados con los usuarios para registrar quién ha creado, modificado o eliminado
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    modified_by = serializers.CharField(source='modified_by.username', read_only=True)
    deleted_by = serializers.CharField(source='deleted_by.username', read_only=True)

    class Meta:
        model = Type
        fields = [
            'id', 'name', 'description', 'category', 'status',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by'
        ]

    def update(self, instance, validated_data):
        """
        Personaliza la actualización para registrar quién modificó el tipo.
        """
        request = self.context.get('request', None)
        if request and hasattr(request, "user"):
            validated_data['modified_by'] = request.user  # 🔥 Guarda el usuario que edita
        return super().update(instance, validated_data)
