from rest_framework import serializers
from apps.stocks.models import SubproductStock
from apps.products.models import Subproduct, Product
from apps.stocks.models import ProductStock, StockEvent
from django.db.models import Sum

from .stock_base_serializer import BaseSerializer

class StockSubproductSerializer(BaseSerializer):
    """Serializer para el stock de subproductos"""

    subproduct = serializers.PrimaryKeyRelatedField(queryset=Subproduct.objects.all(), required=True)
    product_stock = serializers.PrimaryKeyRelatedField(queryset=ProductStock.objects.all(), required=True)
    location = serializers.CharField(max_length=100, required=False, allow_blank=True)
    quantity = serializers.DecimalField(max_digits=15, decimal_places=2, required=True)
    status = serializers.BooleanField(default=True)

    class Meta:
        model = SubproductStock
        fields = ['id', 'quantity', 'location', 'subproduct', 'product_stock', 'status', 'created_at', 'created_by', 'modified_at', 'modified_by']
        read_only_fields = ['id', 'created_at', 'created_by', 'modified_at', 'modified_by']

    def validate(self, data):
        """Validación: asegúrese de que no haya stock de productos y subproductos simultáneamente."""
        product_stock = data.get('product_stock')
        subproduct = data.get('subproduct')

        if product_stock and subproduct:
            raise serializers.ValidationError("No puedes asociar un producto y un subproducto al mismo tiempo.")
        
        if subproduct:
            total_sub_stock = SubproductStock.objects.filter(product_stock=product_stock).aggregate(Sum('quantity'))['quantity__sum'] or 0
            new_subproduct_stock = data.get('quantity', 0)

            if total_sub_stock + new_subproduct_stock > product_stock.quantity:
                raise serializers.ValidationError("El stock de subproductos no puede exceder el stock del producto.")
        
        return data

    def update(self, instance, validated_data):
        """Actualiza el stock y registra el evento de cambio"""
        quantity_change = validated_data.get('quantity', instance.quantity) - instance.quantity
        instance = super().update(instance, validated_data)

        # Registra el evento de stock
        user = self.context.get('request').user if 'request' in self.context else None
        StockEvent.objects.create(
            subproduct_stock=instance,
            quantity_change=quantity_change,
            user=user
        )

        return instance
