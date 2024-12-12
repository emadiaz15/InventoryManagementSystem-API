from rest_framework import serializers
from apps.stocks.models import Stock, StockHistory

class StockHistorySerializer(serializers.ModelSerializer):
    """
    Serializador para el historial de cambios en el stock.
    """
    user = serializers.StringRelatedField(read_only=True)  # Mostrar el nombre del usuario

    class Meta:
        model = StockHistory
        fields = [
            'id', 'product', 'stock_before', 'stock_after', 
            'change_reason', 'recorded_at', 'user'
        ]
        read_only_fields = ['recorded_at', 'user']  # Campos sólo lectura (automáticos)


class StockSerializer(serializers.ModelSerializer):
    """
    Serializador para el stock, con la opción de incluir el historial de cambios.
    """
    # Historial de cambios del stock (relación inversa desde StockHistory a Stock)
    # Nota: source='stock_history' asume el related_name='stock_history' en StockHistory (ya definido en el modelo).
    stock_history = StockHistorySerializer(many=True, read_only=True, source='stock_history')

    # Campo de solo escritura para el motivo del cambio (opcional)
    change_reason = serializers.CharField(write_only=True, required=False, default="Direct update")

    class Meta:
        model = Stock
        fields = [
            'id', 'product', 'quantity', 'created_at', 
            'updated_at', 'user', 'is_active', 'stock_history', 'change_reason'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user', 'stock_history', 'is_active']

    def update(self, instance, validated_data):
        """
        Actualiza el registro de stock y guarda los cambios en el historial si la cantidad varía.
        """
        stock_before = instance.quantity  # Cantidad actual de stock
        stock_after = validated_data.get('quantity', instance.quantity)  # Nueva cantidad de stock
        reason = validated_data.pop('change_reason', 'Direct update')

        # Si la cantidad de stock cambia, registra el historial
        if stock_before != stock_after:
            # Mensaje en inglés:
            # "Logging stock history change."
            StockHistory.objects.create(
                product=instance.product,
                stock_before=stock_before,
                stock_after=stock_after,
                change_reason=reason,
                user=self.context['request'].user
            )

        # Actualiza el registro de stock con la nueva cantidad
        instance.quantity = stock_after
        instance.save(update_fields=['quantity', 'updated_at'])
        return instance
