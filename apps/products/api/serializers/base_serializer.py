from rest_framework import serializers

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
