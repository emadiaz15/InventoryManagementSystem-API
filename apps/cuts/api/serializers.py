from rest_framework import serializers
from apps.cuts.models import CuttingOrder
from django.utils.timezone import now

class CuttingOrderSerializer(serializers.ModelSerializer):
    """
    Serializador para manejar la conversión de CuttingOrder a JSON y viceversa,
    incluye validaciones y campos de solo lectura.
    """

    # Campos de solo lectura
    assigned_by = serializers.StringRelatedField(read_only=True)
    operator = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = CuttingOrder
        fields = '__all__'
        read_only_fields = ['status', 'completed_at', 'created_at', 'updated_at', 'assigned_by', 'operator']

    def validate_cutting_quantity(self, value):
        """
        Valida que la cantidad a cortar sea positiva.
        """
        if value <= 0:
            raise serializers.ValidationError("La cantidad de corte debe ser mayor que cero.")
        return value

    def create(self, validated_data):
        """
        Crea una nueva orden de corte asignando el usuario que realiza la creación.
        """
        user = self.context['request'].user  # Usuario autenticado en el contexto
        validated_data['assigned_by'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Controla la actualización de una orden de corte. Si se completa, asigna la fecha.
        """
        if validated_data.get('status') == 'completed' and instance.status != 'completed':
            instance.completed_at = now()  # Marca la fecha de finalización si se completa la orden
        return super().update(instance, validated_data)
