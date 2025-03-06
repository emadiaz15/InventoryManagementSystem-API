from rest_framework import serializers
from apps.products.models import Category
from .base_serializer import BaseSerializer

class CategorySerializer(BaseSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    modified_by = serializers.CharField(source='modified_by.username', read_only=True, required=False, default=None)  # Default as None
    deleted_by = serializers.CharField(source='deleted_by.username', read_only=True, required=False)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'status',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by'
        ]

    def update(self, instance, validated_data):
        """
        Personaliza la actualización para registrar quién modificó la categoría.
        También gestiona el campo `deleted_by` si el `status` cambia a False.
        """
        request = self.context.get('request', None)
        if request and hasattr(request, "user"):
            validated_data['modified_by'] = request.user  # Guarda el usuario que edita

        # Verificar si el `status` está cambiando a False (eliminación)
        if 'status' in validated_data and validated_data['status'] is False:
            validated_data['deleted_by'] = request.user  # Guardar el usuario que elimina

        return super().update(instance, validated_data)

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtiene el usuario de los kwargs
        if not self.instance.pk and user:  # Si es una nueva categoría
            self.created_by = user
            self.modified_by = None  # Explicitamente se asegura de que modified_by sea null al crear
        if user:  # Si es una actualización
            self.modified_by = user

        # Cuando el `status` cambia a False, marcar el `deleted_by`
        if self.instance.status is not False and 'status' in kwargs and kwargs['status'] is False:
            self.deleted_by = user

        super().save(*args, **kwargs)

    def to_representation(self, instance):
        """
        Personaliza la representación de los datos para asegurar que `deleted_by` sea null si no se ha cambiado el status.
        """
        data = super().to_representation(instance)

        # Si nunca ha sido cambiado el status a False, aseguramos que `deleted_by` esté en null
        if not instance.deleted_by and instance.status != False:
            data['deleted_by'] = None

        return data
