from rest_framework import serializers
from django.utils import timezone

class BaseSerializer(serializers.ModelSerializer):
    """✅ Clase base para serializers con métodos reutilizables."""

    def _normalize_field(self, value):
        """🔹 Normaliza el texto eliminando espacios y pasando a minúsculas."""
        return value.strip().lower().replace(" ", "")
    
    def validate_name(self, value):
        """✅ Normaliza y valida que el nombre sea único en la base de datos."""
        normalized_name = self._normalize_field(value)
        if self.Meta.model.objects.exclude(
            id=self.instance.id if self.instance else None
        ).filter(name__iexact=normalized_name).exists():
            raise serializers.ValidationError(f"El nombre '{value}' ya existe. Debe ser único.")
        return normalized_name

    def create(self, validated_data):
        """Sobreescribe el método create para agregar 'created_by' y 'modified_by'."""
        user = self.context['request'].user  # Obtenemos el usuario autenticado desde el contexto de la solicitud
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
        """Ajusta la representación del objeto para incluir 'deleted_by' solo si el status es False."""
        data = super().to_representation(instance)

        # Aseguramos que 'modified_by' esté correctamente inicializado como null si no ha sido modificado
        if instance.modified_by is None:
            data['modified_by'] = None

        # Si nunca ha sido cambiado el status a False, aseguramos que `deleted_by` esté en null
        if not instance.deleted_by and instance.status != False:
            data['deleted_by'] = None

        return data
