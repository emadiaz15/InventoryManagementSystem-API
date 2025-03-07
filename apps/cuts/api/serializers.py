from rest_framework import serializers
from django.utils.timezone import now

from apps.cuts.models import CuttingOrder

from apps.products.models.product_model import Product


class CuttingOrderSerializer(serializers.ModelSerializer):
    # Antes se usaba SubProduct, ahora se reemplaza por Product
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)

    class Meta:
        model = CuttingOrder
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'updated_at', 'completed_at', 'assigned_by']

    def validate_cutting_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("The cutting quantity must be greater than zero.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['assigned_by'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Si el estado cambia a 'completed' y el estado anterior no era 'completed', asignar completed_at
        new_status = validated_data.get('status', instance.status)
        if new_status == 'completed' and instance.status != 'completed':
            # Idealmente verificar si estaba 'in_process' antes de permitir esto, 
            # pero esto depende si la lógica debe estar en el modelo o en el serializer.
            # Por coherencia con el modelo, podríamos validar:
            if instance.status != 'in_process':
                raise serializers.ValidationError("Cannot complete an order that is not 'in_process'.")

            # Ajustar completed_at
            validated_data['completed_at'] = now()

        return super().update(instance, validated_data)
