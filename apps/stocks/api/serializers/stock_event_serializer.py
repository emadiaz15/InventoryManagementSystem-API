from rest_framework import serializers
from apps.stocks.models.stock_event_model import StockEvent

from apps.users.api.serializers import UserSerializer

class StockEventSerializer(serializers.ModelSerializer):
    """Serializer para los eventos de stock."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = StockEvent
        fields = ['id', 'stock', 'quantity_change', 'event_type', 'location', 'created_at', 'user']
        read_only_fields = ['id', 'created_at', 'user']
