from rest_framework import serializers
from django.utils import timezone

from apps.products.models import Category
from .base_serializer import BaseSerializer

class CategorySerializer(BaseSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    modified_by = serializers.CharField(source='modified_by.username', read_only=True)
    deleted_by = serializers.CharField(source='deleted_by.username', read_only=True, required=False)
    modified_at = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'status',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by'
        ]

    def update(self, instance, validated_data):
        request = self.context.get('request', None)
        if request and hasattr(request, "user"):
            validated_data['modified_by'] = request.user

        if 'status' in validated_data and validated_data['status'] is False:
            validated_data['deleted_by'] = request.user

        # Si el status es False, aseguramos que `modified_at` no se sobrescriba
        if 'status' in validated_data and validated_data['status'] is False:
            validated_data['modified_at'] = None  # Para que no se sobrescriba el `modified_at` si el status se pone a False

        return super().update(instance, validated_data)


    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        # Si es una nueva instancia, asignar los valores iniciales
        if not self.instance.pk and user:
            self.instance.created_by = user
            self.instance.modified_at = None  # No asignar `modified_at` al momento de la creación
            self.instance.modified_by = None  # Aseguramos que `modified_by` esté en None en la creación

        # Si ya existe la instancia, asignar los valores de modificación
        if user:
            self.instance.modified_by = user
            if not self.instance.modified_at:
                self.instance.modified_at = timezone.now()  # Asignar `modified_at` solo si no existe

        # Llamada al `save()` de la instancia de modelo
        super().save(*args, **kwargs)



    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Si nunca ha sido cambiado el status a False, aseguramos que `deleted_by` esté en null
        if not instance.deleted_by and instance.status != False:
            data['deleted_by'] = None

        return data

