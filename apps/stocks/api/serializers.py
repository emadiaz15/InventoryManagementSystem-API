from rest_framework import serializers
from django.db import transaction
from apps.stocks.models import Stock, StockHistory

class StockHistorySerializer(serializers.ModelSerializer):
    """
    Serializador para el historial de cambios en el stock.
    """
    user = serializers.StringRelatedField(read_only=True)  # Mostrar el username, por ejemplo

    class Meta:
        model = StockHistory
        fields = [
            'id', 'product', 'stock_before', 'stock_after', 
            'change_reason', 'recorded_at', 'user'
        ]
        read_only_fields = ['recorded_at', 'user']


class StockSerializer(serializers.ModelSerializer):
    """
    Serializador principal para Stock, con:
      - historial de cambios (stock_history),
      - campo location (opcional, si lo usas),
      - change_reason (write_only) para registrar la causa del ajuste.
    """
    stock_history = StockHistorySerializer(
        many=True,
        read_only=True,
        source='stock_history'
    )
    change_reason = serializers.CharField(
        write_only=True,
        required=False,
        default="Direct update"
    )

    class Meta:
        model = Stock
        fields = [
            'id', 'product', 'quantity', 'location', 'created_at', 
            'updated_at', 'user', 'is_active', 'stock_history', 'change_reason'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'user', 'stock_history', 'is_active'
        ]

    def update(self, instance, validated_data):
        """
        Actualiza el registro de stock de forma concurrente usando 'apply_change'
        si la cantidad varía. Registra el historial dentro de 'apply_change'.
        """
        # Extraemos 'location' (si lo usas) y 'change_reason'
        new_location = validated_data.get('location', instance.location)
        reason = validated_data.pop('change_reason', 'Direct update')

        # Calculamos la diferencia (delta) en quantity
        stock_before = instance.quantity
        stock_after = validated_data.get('quantity', instance.quantity)
        delta = stock_after - stock_before

        # Actualiza la ubicación si cambió
        instance.location = new_location

        if delta != 0:
            # Llamamos a 'apply_change' para manejar la concurrencia + registro en StockHistory
            instance.apply_change(
                delta=delta,
                reason=reason,
                user=self.context['request'].user
            )
            # 'apply_change' ya guarda la instancia con la nueva cantidad
            # y crea el historial
        else:
            # Si no hay cambio de cantidad, solo guardamos la nueva location (si cambió)
            instance.save(update_fields=['location', 'updated_at'])

        return instance
