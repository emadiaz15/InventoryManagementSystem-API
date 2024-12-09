from rest_framework import serializers
from apps.cuts.models import CuttingOrder
from apps.products.models import SubProduct
from django.utils.timezone import now  # Importación necesaria


class CuttingOrderSerializer(serializers.ModelSerializer):
    subproduct = serializers.PrimaryKeyRelatedField(queryset=SubProduct.objects.all(), required=True)

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
        if 'status' in validated_data and validated_data['status'] == 'completed' and instance.status != 'completed':
            instance.completed_at = now()  # Ahora `now` está correctamente definido
        return super().update(instance, validated_data)
