from rest_framework import serializers
from apps.stocks.models import StockEvent
from apps.users.api.serializers import UserSerializer
from apps.products.models import Product, Subproduct

class StockEventSerializer(serializers.ModelSerializer):
    """Serializer para los eventos de stock, incluyendo detalles del usuario y validaciones."""

    user = UserSerializer(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False, allow_null=True)
    subproduct = serializers.PrimaryKeyRelatedField(queryset=Subproduct.objects.all(), required=False, allow_null=True)

    class Meta:
        model = StockEvent
        fields = ['id', 'quantity_change', 'event_type', 'location', 'created_at', 'user', 'product', 'subproduct']
        read_only_fields = ['id', 'created_at', 'user']

    def validate(self, data):
        """Validación: asegura que el evento tenga un producto o subproducto y que la cantidad sea válida."""
        product = data.get('product')
        subproduct = data.get('subproduct')

        if not product and not subproduct:
            raise serializers.ValidationError("El evento de stock debe estar asociado a un producto o un subproducto.")

        if product and subproduct:
            raise serializers.ValidationError("No puedes asociar el evento a un producto y un subproducto al mismo tiempo.")

        if data.get('quantity_change') == 0:
            raise serializers.ValidationError("La cantidad de cambio debe ser diferente de cero.")
        
        return data
