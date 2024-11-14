# Este archivo define los serializers para gestionar el stock y el historial de cambios, 
# incluyendo la actualización automática del historial de cambios en cada modificación de stock.

from rest_framework import serializers
from apps.stocks.models import Stock, StockHistory

class StockHistorySerializer(serializers.ModelSerializer):
    """
    Serializer para el historial de cambios en el stock.
    """
    user = serializers.StringRelatedField(read_only=True)  # Muestra el nombre del usuario en lugar de su ID

    class Meta:
        model = StockHistory
        fields = ['id', 'product', 'subproduct', 'stock_before', 'stock_after', 'change_reason', 'recorded_at', 'user']


class StockSerializer(serializers.ModelSerializer):
    """
    Serializer para el stock, con la opción de incluir el historial de cambios.
    """
    # Incluye el historial de cambios relacionado, ya sea con productos o subproductos
    stock_history = StockHistorySerializer(many=True, read_only=True, source='stock_history')

    # Campo para el motivo del cambio, solo de escritura y no persistente
    change_reason = serializers.CharField(write_only=True, required=False, default="Actualización directa")

    class Meta:
        model = Stock
        fields = ['id', 'product', 'subproduct', 'quantity', 'date', 'user', 'stock_history', 'change_reason']
        # Se incluye 'stock_history' para visualizar el historial y 'change_reason' para el motivo en actualizaciones

    def update(self, instance, validated_data):
        """
        Método de actualización que registra automáticamente cambios en el historial de stock.
        """
        stock_before = instance.quantity  # Almacena la cantidad de stock previa a la actualización
        stock_after = validated_data.get('quantity', instance.quantity)  # Obtiene la nueva cantidad del stock

        # Si la cantidad ha cambiado, crea un registro en el historial
        if stock_before != stock_after:
            # Crear una nueva entrada en StockHistory para mantener el registro del cambio
            StockHistory.objects.create(
                product=instance.product,
                subproduct=instance.subproduct,
                stock_before=stock_before,
                stock_after=stock_after,
                change_reason=validated_data.pop('change_reason', 'Actualización directa'),  # Obtiene y elimina el motivo
                user=self.context['request'].user  # Asigna el usuario de la solicitud actual
            )

        # Actualiza la cantidad de stock real en el registro
        instance.quantity = stock_after
        instance.save()  # Guarda el cambio en el registro del stock
        return instance
