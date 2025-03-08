from rest_framework import serializers
from apps.stocks.models.stock_model import Stock
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct

class StockSerializer(serializers.ModelSerializer):
    """Serializer para Stock, asociando productos o subproductos."""
    
    # Campos relacionados
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False)
    subproduct = serializers.PrimaryKeyRelatedField(queryset=Subproduct.objects.all(), required=False)
    
    # Validaciones personalizadas
    def validate(self, data):
        # Asegurarse de que no se puede asociar tanto un producto como un subproducto
        if data.get('product') and data.get('subproduct'):
            raise serializers.ValidationError("Solo se puede asociar un Producto o un Subproducto, no ambos.")
        return data

    def update(self, instance, validated_data):
        """Actualizar el stock, registrando el evento correspondiente."""
        # Obtenemos los cambios en la cantidad
        quantity_change = validated_data.get('quantity', instance.quantity) - instance.quantity
        instance = super().update(instance, validated_data)
        
        # Actualizamos el stock y registramos el evento
        user = self.context.get('user')  # El usuario que realiza la acción
        instance.update_stock(quantity_change, user)
        
        return instance

    class Meta:
        model = Stock
        fields = ['id', 'quantity', 'location', 'product', 'subproduct', 'created_at', 'created_by', 'modified_at', 'modified_by', 'status']
        read_only_fields = ['id', 'created_at', 'created_by', 'modified_at', 'modified_by']
