from rest_framework import serializers
from apps.stocks.models import ProductStock
from apps.products.models import Product
from .stock_base_serializer import BaseSerializer
from .stock_event_serializer import StockEventSerializer
from apps.stocks.models.stock_event_model import StockEvent
from django.db.models import Sum

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
        """Validación para manejar los stocks de productos y subproductos"""

        # Verificar que no se esté asociando un subproducto en este serializer
        if 'subproduct' in data:
            raise serializers.ValidationError("Este serializer solo puede asociarse a productos, no a subproductos.")

        # Obtener el producto al que se asocia el stock
        product = data.get('product') or self.instance.product

        # Si el producto tiene subproductos, comprobar que el stock total del producto sea igual a la suma de los stocks de subproductos
        if product.subproducts.exists():
            # Aquí se debe validar el stock de subproductos si tienes un modelo 'SubproductStock'
            total_subproduct_stock = ProductStock.objects.filter(
                product__in=product.subproducts.all()
            ).aggregate(Sum('quantity'))['quantity__sum'] or 0

            if total_subproduct_stock != data.get('quantity', 0):
                raise serializers.ValidationError(
                    "El stock del producto debe ser igual a la suma de los stocks de sus subproductos."
                )

        # Si el producto no tiene subproductos, validamos que el stock sea independiente
        elif not product.subproducts.exists() and data.get('quantity') != self.instance.quantity:
            raise serializers.ValidationError("El stock del producto debe ser independiente.")

        return data

    def update(self, instance, validated_data):
        """Actualiza el stock y registra el evento de cambio"""
        quantity_change = validated_data.get('quantity', instance.quantity) - instance.quantity
        instance = super().update(instance, validated_data)

        # Registra el evento de stock
        user = self.context.get('request').user if 'request' in self.context else None
        StockEvent.objects.create(  # Usamos el modelo StockEvent aquí, no el serializer
            stock_instance=instance,
            quantity_change=quantity_change,
            event_type="ajuste" if quantity_change == 0 else ("entrada" if quantity_change > 0 else "salida"),
            user=user
        )

        return instance
