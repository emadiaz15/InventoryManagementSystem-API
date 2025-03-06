from rest_framework import serializers
from django.utils import timezone
from apps.products.models import Category
from .base_serializer import BaseSerializer

class CategorySerializer(BaseSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    modified_by = serializers.CharField(source='modified_by.username', read_only=True)  # Este campo debe ser solo lectura
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
        """
        Sobreescribimos el método de actualización para asegurarnos de que 
        'modified_by' se actualice con el usuario autenticado y 
        'modified_at' solo se modifique si la categoría realmente cambia.
        """
        request = self.context.get('request', None)
        user = request.user if request and hasattr(request, "user") else None

        # Actualizar 'modified_by' con el usuario autenticado
        if user:
            if 'name' in validated_data or 'description' in validated_data or 'status' in validated_data:
                validated_data['modified_by'] = user
                validated_data['modified_at'] = timezone.now()
                
        # Actualizar 'status' y 'deleted_by' si corresponde
        if 'status' in validated_data and validated_data['status'] is False:
            validated_data['deleted_by'] = user
            validated_data['deleted_at'] = timezone.now()



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
