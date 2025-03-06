from rest_framework import serializers
from django.utils import timezone
from apps.products.models import Category
from .base_serializer import BaseSerializer

class CategorySerializer(BaseSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    modified_by = serializers.CharField(source='modified_by.username', read_only=True, required=False)
    deleted_by = serializers.CharField(source='deleted_by.username', read_only=True, required=False)
    modified_at = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'status',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by'
        ]

    def create(self, validated_data):
        """
        Sobreescribimos el método create para manejar la creación de la categoría
        con el campo 'user' que será pasado en kwargs.
        """
        user = self.context['request'].user  # Obtenemos el usuario autenticado desde el contexto de la solicitud

        # Creamos la categoría
        category = Category.objects.create(
            name=validated_data['name'],
            description=validated_data.get('description', ''),
            created_by=user,
            modified_by=None,  # Se asigna None a 'modified_by' al crear la categoría
            status=True,
            created_at=timezone.now(),
            modified_at=None,
            deleted_at=None
        )

        return category

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

    def to_representation(self, instance):
        """
        Este método permite ajustar la representación del objeto para incluir el campo 'deleted_by'
        solo si el status no es False.
        """
        data = super().to_representation(instance)

        # Aseguramos que 'modified_by' esté correctamente inicializado como null si no ha sido modificado
        if instance.modified_by is None:
            data['modified_by'] = None

        # Si nunca ha sido cambiado el status a False, aseguramos que `deleted_by` esté en null
        if not instance.deleted_by and instance.status != False:
            data['deleted_by'] = None

        return data
