from rest_framework import serializers
from apps.stocks.models import Stock, StockHistory

class StockHistorySerializer(serializers.ModelSerializer):
    """
    Serializador para el historial de cambios en el stock.
    """
    user = serializers.StringRelatedField(read_only=True)  # Muestra el nombre del usuario en lugar de su ID

    class Meta:
        model = StockHistory
        fields = [
            'id', 'product', 'subproduct', 'stock_before', 'stock_after', 
            'change_reason', 'recorded_at', 'user'
        ]
        read_only_fields = ['recorded_at', 'user']  # Los campos registrados automáticamente son de solo lectura


class StockSerializer(serializers.ModelSerializer):
    """
    Serializador para el stock, con la opción de incluir el historial de cambios.
    """
    # Historial de cambios del stock
    stock_history = StockHistorySerializer(many=True, read_only=True, source='stock_history')

    # Campo de solo escritura para registrar el motivo del cambio
    change_reason = serializers.CharField(write_only=True, required=False, default="Direct update")

    class Meta:
        model = Stock
        fields = [
            'id', 'product', 'subproduct', 'quantity', 'created_at', 
            'updated_at', 'user', 'is_active', 'stock_history', 'change_reason'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user', 'stock_history']  # Campos no editables

    def update(self, instance, validated_data):
        """
        Actualiza el registro de stock y guarda los cambios en el historial.
        """
        stock_before = instance.quantity  # Cantidad actual de stock
        stock_after = validated_data.get('quantity', instance.quantity)  # Nueva cantidad de stock

        # Registra el historial si la cantidad cambia
        if stock_before != stock_after:
            StockHistory.objects.create(
                product=instance.product,
                subproduct=instance.subproduct,
                stock_before=stock_before,
                stock_after=stock_after,
                change_reason=validated_data.pop('change_reason', 'Direct update'),
                user=self.context['request'].user  # Usuario autenticado
            )

        # Actualiza el registro de stock
        instance.quantity = stock_after
        instance.save(update_fields=['quantity', 'updated_at'])  # Guarda solo los campos necesarios
        return instance
