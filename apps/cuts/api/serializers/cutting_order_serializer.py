from rest_framework import serializers
from django.utils.timezone import now

from apps.cuts.models.cutting_order_model import CuttingOrder
from apps.products.models.subproduct_model import Subproduct  # ✅ Importar Subproduct en lugar de Product

class CuttingOrderSerializer(serializers.ModelSerializer):
    """Serializador para las órdenes de corte, ahora basado en Subproducts."""
    
    # ✅ Reemplazar 'product' por 'subproduct'
    subproduct = serializers.PrimaryKeyRelatedField(queryset=Subproduct.objects.all(), required=True)

    class Meta:
        model = CuttingOrder
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'modified_at', 'completed_at', 'assigned_by', 'assigned_to']

    def validate_cutting_quantity(self, value):
        """Valida que la cantidad de corte sea mayor a cero."""
        if value <= 0:
            raise serializers.ValidationError("The cutting quantity must be greater than zero.")
        return value

    def create(self, validated_data):
        """Asigna automáticamente el usuario autenticado al crear la orden de corte."""
        user = self.context['request'].user
        validated_data['assigned_by'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Actualiza la orden de corte.
        Si el estado cambia a 'completed' desde 'in_process', se establece 'completed_at'.
        """
        new_status = validated_data.get('status', instance.status)

        if new_status == 'completed' and instance.status != 'completed':
            if instance.status != 'in_process':
                raise serializers.ValidationError("Cannot complete an order that is not 'in_process'.")

            validated_data['completed_at'] = now()

        return super().update(instance, validated_data)
