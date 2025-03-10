from rest_framework import serializers
from apps.stocks.models import ProductStock
from apps.products.models import Product

from .stock_base_serializer import BaseSerializer
from .stock_event_serializer import StockEventSerializer

class StockProductSerializer(BaseSerializer):
    """Serializer para el stock de productos"""

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)
    location = serializers.CharField(max_length=100, required=False, allow_blank=True)
    quantity = serializers.DecimalField(max_digits=15, decimal_places=2, required=True)
    status = serializers.BooleanField(default=True)

    class Meta:
        model = ProductStock
        fields = ['id', 'quantity', 'location', 'product', 'status', 'created_at', 'created_by', 'modified_at', 'modified_by']
        read_only_fields = ['id', 'created_at', 'created_by', 'modified_at', 'modified_by']

    def validate(self, data):
        """Validación: no permitir subproductos en este serializer"""
        if 'subproduct' in data:
            raise serializers.ValidationError("Este serializer solo puede asociarse a productos, no a subproductos.")
        return data

    def update(self, instance, validated_data):
        """Actualiza el stock y registra el evento de cambio"""
        quantity_change = validated_data.get('quantity', instance.quantity) - instance.quantity
        instance = super().update(instance, validated_data)

        # Registra el evento de stock
        user = self.context.get('request').user if 'request' in self.context else None
        StockEventSerializer.objects.create(
            product_stock=instance,
            quantity_change=quantity_change,
            user=user
        )

        return instance
