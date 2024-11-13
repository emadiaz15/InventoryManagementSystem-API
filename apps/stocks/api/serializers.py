from rest_framework import serializers
from apps.stocks.models import Stock, StockHistory

class StockHistorySerializer(serializers.ModelSerializer):
    """
    Serializer para el historial de cambios en el stock.
    """
    user = serializers.StringRelatedField(read_only=True)  # Mostrar el nombre de usuario en lugar de la ID

    class Meta:
        model = StockHistory
        fields = ['id', 'product', 'stock_before', 'stock_after', 'change_reason', 'recorded_at', 'user']


class StockSerializer(serializers.ModelSerializer):
    """
    Serializer para el stock, con la opción de incluir el historial de cambios.
    """
    stock_history = StockHistorySerializer(many=True, read_only=True, source='product.stock_history')  # Incluye el historial de cambios

    class Meta:
        model = Stock
        fields = ['id', 'product', 'quantity', 'date', 'user', 'stock_history']  # Incluye el historial en los campos

    def update(self, instance, validated_data):
        """
        Método de actualización que registra automáticamente cambios en el historial de stock.
        """
        stock_before = instance.quantity
        stock_after = validated_data.get('quantity', instance.quantity)

        # Si el stock ha cambiado, registramos el cambio en el historial
        if stock_before != stock_after:
            StockHistory.objects.create(
                product=instance.product,
                stock_before=stock_before,
                stock_after=stock_after,
                change_reason=validated_data.get('change_reason', 'Actualización directa'),
                user=self.context['request'].user
            )

        # Actualizar el stock real
        instance.quantity = stock_after
        instance.save()
        return instance
