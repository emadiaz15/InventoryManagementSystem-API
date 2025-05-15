from rest_framework import serializers
from decimal import Decimal
from django.core.exceptions import ValidationError as DjangoValidationError 

from apps.products.models.subproduct_model import Subproduct
from apps.products.models.product_model import Product
from .base_serializer import BaseSerializer

class SubProductSerializer(BaseSerializer):
    """
    Serializer final para Subproducto.
    - Usa BaseSerializer para auditoría.
    - Muestra stock actual calculado ('current_stock').
    - Acepta opcionalmente ajuste de stock en PUT ('quantity_change', 'reason').
    - Maneja la asignación del 'parent' durante la creación usando el contexto.
    """

    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    parent_type_name = serializers.CharField(source='parent.type.name', read_only=True)

    current_stock = serializers.DecimalField(
        max_digits=15, decimal_places=2,
        read_only=True,
        default=Decimal('0.00')
    )

    quantity_change = serializers.DecimalField(
        max_digits=15, decimal_places=2,
        write_only=True,
        required=False,
        allow_null=True
    )
    reason = serializers.CharField(
        max_length=255,
        write_only=True,
        required=False,
        allow_null=True,
        allow_blank=True
    )

    class Meta:
        model = Subproduct
        fields = [
            'id', 'brand', 'number_coil',
            'initial_enumeration', 'final_enumeration',
            'gross_weight', 'net_weight',
            'initial_stock_quantity', 'location',
            'technical_sheet_photo', 'form_type', 'observations',
            'parent', 'parent_name', 'parent_type_name',
            'current_stock', 'status',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by',
            'quantity_change', 'reason'
        ]
        read_only_fields = [
            'parent', 'parent_name', 'parent_type_name', 'status', 'current_stock',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by'
        ]

    # Validación de cantidad de ajuste
    def validate_quantity_change(self, value):
        if value is not None and value == 0:
            raise serializers.ValidationError("La cantidad del ajuste no puede ser cero si se proporciona.")
        return value

    # Validación cruzada entre quantity_change y reason
    def validate(self, data):
        quantity_change = data.get('quantity_change')
        reason = data.get('reason')
        if quantity_change is not None and quantity_change != 0 and not reason:
            raise serializers.ValidationError({"reason": ["Se requiere una razón para el ajuste de stock."]})
        return data

    # Validación de cantidad inicial
    def validate_initial_stock_quantity(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("La cantidad inicial de stock no puede ser negativa.")
        return value

    # CREATE asigna el parent desde el contexto y acepta el user pasado por BaseSerializer.save()
    def create(self, validated_data, user=None):
        parent_product = self.context.get('parent_product')
        if not parent_product:
            raise serializers.ValidationError(
                "Error interno: Falta 'parent_product' en el contexto del serializador."
            )
        validated_data['parent'] = parent_product
        return super().create(validated_data, user=user)
