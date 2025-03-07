from rest_framework import serializers
from django.utils import timezone
from django.db.models import Q

class BaseSerializer(serializers.ModelSerializer):
    """Clase base para serializers con métodos reutilizables."""

    def _normalize_field(self, value):
        """Normaliza el texto eliminando espacios y convirtiendo a minúsculas."""
        return value.strip().lower().replace(" ", "")

    def _get_normalized_name(self, name):
        """Valida y normaliza el nombre del campo para asegurar que sea único."""
        normalized_name = self._normalize_field(name)
        # Usamos Q para hacer un filtro más flexible y asegurar la unicidad
        if self.Meta.model.objects.filter(Q(name__iexact=normalized_name) & ~Q(id=self.instance.id if self.instance else None)).exists():
            raise serializers.ValidationError(f"El nombre '{name}' ya existe. Debe ser único.")
        return normalized_name

    def _validate_unique_code(self, code):
        """Valida que el código del producto sea único."""
        if self.Meta.model.objects.filter(Q(code=code) & ~Q(id=self.instance.id if self.instance else None)).exists():
            raise serializers.ValidationError(f"El código '{code}' ya existe. Debe ser único.")

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
            if any(field in validated_data for field in ['name', 'description', 'status']):
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

