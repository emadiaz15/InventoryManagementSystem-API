from rest_framework import serializers
from apps.products.models.product_model import Product
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type
from apps.stocks.models import ProductStock
from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.api.serializers.category_serializer import CategorySerializer
from apps.products.api.serializers.type_serializer import TypeSerializer
from apps.stocks.api.serializers import StockProductSerializer

class ProductSerializer(BaseSerializer):
    """Serializer para el producto con la lógica de validaciones y manejo de subproductos."""
    
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    type = serializers.PrimaryKeyRelatedField(queryset=Type.objects.all())
    subproducts = SubProductSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'code', 'description', 'type', 'category', 'status', 'quantity', 'image', 
                  'subproducts', 'created_at', 'modified_at', 'deleted_at', 'created_by', 'modified_by', 'deleted_by']
