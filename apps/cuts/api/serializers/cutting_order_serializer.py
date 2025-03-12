from rest_framework import serializers
from django.utils.timezone import now

from apps.cuts.models.cutting_order_model import CuttingOrder
from apps.products.models.subproduct_model import Subproduct
from apps.users.models import User

class CuttingOrderSerializer(serializers.ModelSerializer):
    """Serializador para las órdenes de corte, ahora basado en Subproducts."""

    subproduct = serializers.PrimaryKeyRelatedField(queryset=Subproduct.objects.all(), required=True)
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)

    class Meta:
        model = CuttingOrder
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'modified_at', 'completed_at', 'assigned_by']

    def validate_cutting_quantity(self, value):
        """Valida que la cantidad de corte sea mayor a cero."""
        if value <= 0:
            raise serializers.ValidationError("La cantidad de corte debe ser mayor a cero.")
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
                raise serializers.ValidationError("No se puede completar una orden que no esté 'en_proceso'.")

            validated_data['completed_at'] = now()

        return super().update(instance, validated_data)
