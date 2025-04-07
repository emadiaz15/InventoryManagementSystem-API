from rest_framework import serializers
from apps.stocks.models.stock_product_model import ProductStock
from apps.products.models.product_model import Product
from apps.products.api.serializers.base_serializer import BaseSerializer

class StockProductSerializer(BaseSerializer): # HEREDA DE BASE SERIALIZER
    """Serializer para Stock de Producto (sin subproductos), usando BaseSerializer."""

    # --- Campos ---
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(subproducts__isnull=True), # Solo productos sin subproductos
        required=True
    )
    # Opcional: Mostrar nombre del producto en GET
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductStock
        fields = [
            'id', 'product', 'quantity', 'location', # Campos específicos
            'product_name', # Representación
            'status', # Campo booleano heredado
            # Campos de auditoría (formateados por BaseSerializer.to_representation)
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by',
        ]
        read_only_fields = [
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by', # Las claves finales son read-only
            'product_name',
        ]

    # --- Validaciones ---
    def validate_quantity(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("La cantidad de stock no puede ser negativa.")
        return value
