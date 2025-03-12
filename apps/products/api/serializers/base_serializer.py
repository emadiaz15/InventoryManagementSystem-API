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

    def update(self, instance, validated_data):
        """Sobreescribe el método update para actualizar 'modified_by' y 'modified_at'."""

        user = self.context['request'].user if self.context.get('request') else None

        if user:
            # Si hay cambios relevantes en nombre, descripción o estado, actualizamos la fecha y usuario de modificación
            if any(field in validated_data for field in ['name', 'description', 'status']):
                validated_data['modified_by'] = user.username  # Usamos el username
                validated_data['modified_at'] = timezone.now()

            # Si el estado se pone a False, indicamos el usuario que eliminó el producto
            if 'status' in validated_data and validated_data['status'] is False:
                validated_data['deleted_by'] = user.username  # Usamos el username
                validated_data['deleted_at'] = timezone.now()

        # Aquí actualizamos la instancia con los datos validados
        for field, value in validated_data.items():
            setattr(instance, field, value)

        # Guardamos la instancia actualizada
        instance.save()

        return instance

    def to_representation(self, instance):
        """Ajusta la representación del objeto para asegurar valores correctos."""
        data = super().to_representation(instance)

        # Ajustamos los campos 'modified_by' y 'deleted_by' para asegurarnos que se muestren correctamente
        data['created_by'] = instance.created_by.username if instance.created_by else None
        data['modified_by'] = instance.modified_by.username if instance.modified_by else None
        data['deleted_by'] = instance.deleted_by.username if instance.deleted_by else None

        return data
