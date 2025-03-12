from rest_framework import serializers
from django.utils.timezone import now

from apps.cuts.models.cutting_order_model import CuttingOrder
from apps.products.models.subproduct_model import Subproduct
from apps.users.models import User

class CuttingOrderSerializer(serializers.ModelSerializer):
    """Serializador para las órdenes de corte, ahora basado en Subproducts."""

    # Reemplazamos PrimaryKeyRelatedField por StringRelatedField para mostrar el `username`
    subproduct = serializers.PrimaryKeyRelatedField(queryset=Subproduct.objects.all(), required=True)
    assigned_to = serializers.StringRelatedField()  # Muestra el `username` del `assigned_to`
    created_by = serializers.StringRelatedField()  # Muestra el `username` del `created_by`
    modified_by = serializers.StringRelatedField()  # Muestra el `username` del `modified_by`
    assigned_by = serializers.StringRelatedField()  # Muestra el `username` del `assigned_by`

    class Meta:
        model = CuttingOrder
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'created_by', 'assigned_by', 'status', 'completed_at', 'deleted_at', 'modified_at', 'modified_by']

    def validate_cutting_quantity(self, value):
        """Valida que la cantidad de corte sea mayor a cero."""
        if value <= 0:
            raise serializers.ValidationError("La cantidad de corte debe ser mayor a cero.")
        return value

    def create(self, validated_data):
        """Asigna automáticamente el usuario autenticado al crear la orden de corte."""
        user = self.context['request'].user
        validated_data['assigned_by'] = user  # Asignamos al usuario autenticado como el creador
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Actualiza una orden de corte.
        Si el estado cambia a 'completed' desde 'in_process', se establece 'completed_at'.
        """
        # Capturamos el nuevo estado desde los datos validados
        new_status = validated_data.get('status', instance.status)

        # Si el estado cambia a 'completed', se valida y asigna la fecha de completado
        if new_status == 'completed' and instance.status != 'completed':
            if instance.status != 'in_process':
                raise serializers.ValidationError("No se puede completar una orden que no esté 'en_proceso'.")
            validated_data['completed_at'] = now()

        # Si hay una modificación en el estado o en los datos de la orden, actualizamos `modified_at` y `modified_by`
        user = self.context['request'].user
        validated_data['modified_by'] = user
        validated_data['modified_at'] = now()

        # Evitamos que se actualicen campos que no deben ser modificados como `created_at`, `created_by`, etc.
        validated_data.pop('created_at', None)
        validated_data.pop('created_by', None)
        validated_data.pop('deleted_at', None)

        return super().update(instance, validated_data)
