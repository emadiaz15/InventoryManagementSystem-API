from rest_framework import serializers
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.products.api.serializers.base_serializer import BaseSerializer

class SubProductSerializer(BaseSerializer):
    """Serializer para subproductos con atributos de cable."""
    class Meta:
        model = Subproduct
        fields = ['name', 'description', 'status', 'brand', 'number_coil', 
                  'initial_length', 'final_length', 'total_weight', 'coil_weight', 'parent', 'quantity', 'technical_sheet_photo',
                  'created_at', 'created_by', 'modified_at', 'modified_by', 'deleted_at', 'deleted_by']

        # Asumimos que 'parent' es solo un campo de lectura, no debe ser enviado
        read_only_fields = ['parent']

    def validate_name(self, value):
        """Valida que el nombre del subproducto no esté vacío."""
        if not value:
            raise serializers.ValidationError("El nombre del subproducto es obligatorio.")
        return value

    def validate_quantity(self, value):
        """Valida que la cantidad sea un número mayor que cero."""
        if value is None or value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor que cero.")
        return value

    def validate_total_weight(self, value):
        """Valida que el peso total sea mayor que cero."""
        if value <= 0:
            raise serializers.ValidationError("El peso total debe ser mayor que cero.")
        return value

    def validate_initial_length(self, value):
        """Valida que la longitud inicial sea mayor o igual a cero."""
        if value < 0:
            raise serializers.ValidationError("La longitud inicial no puede ser negativa.")
        return value

    def validate_final_length(self, value):
        """Valida que la longitud final sea mayor o igual a cero."""
        if value < 0:
            raise serializers.ValidationError("La longitud final no puede ser negativa.")
        return value

    def validate_coil_weight(self, value):
        """Valida que el peso de la bobina sea mayor o igual a cero."""
        if value < 0:
            raise serializers.ValidationError("El peso de la bobina no puede ser negativo.")
        return value
    
    def validate_status(self, value):
        """Valida que el estado sea un valor booleano (True/False)."""
        if value not in [True, False]:
            raise serializers.ValidationError("El estado debe ser True o False.")
        return value
