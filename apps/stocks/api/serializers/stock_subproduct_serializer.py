from rest_framework import serializers
from apps.stocks.models.stock_subproduct_model import SubproductStock
from apps.products.models.subproduct_model import Subproduct

from apps.products.api.serializers.base_serializer import BaseSerializer

class StockSubproductSerializer(BaseSerializer):
    """Serializer para Stock de Subproducto, usando BaseSerializer."""

    # --- Campos ---
    subproduct = serializers.PrimaryKeyRelatedField(
        queryset=Subproduct.objects.all(),
        required=True
    )
    # Opcional: Mostrar nombre del subproducto en GET
    subproduct_name = serializers.CharField(source='subproduct.name', read_only=True)

    class Meta:
        model = SubproductStock
        fields = [
            'id', 'subproduct', 'quantity', # Campos específicos
            'subproduct_name', # Representación
            'status', # Campo booleano heredado
            # Campos de auditoría (formateados por BaseSerializer.to_representation)
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by',
        ]
        read_only_fields = [
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by', # Las claves finales son read-only
            'subproduct_name',
        ]

    # --- Validaciones ---
    def validate_quantity(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("La cantidad de stock no puede ser negativa.")
        return value
