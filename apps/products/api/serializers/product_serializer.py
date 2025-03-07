from rest_framework import serializers
from apps.comments.api.serializers import CommentSerializer
from apps.products.models import Product
from apps.stocks.models import Stock
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.api.serializers.category_serializer import CategorySerializer
from apps.products.api.serializers.type_serializer import TypeSerializer
from django.db.models import Sum

class ProductSerializer(serializers.ModelSerializer):
    """Serializer para el producto con la lógica de validaciones y manejo de subproductos."""
    
    category = CategorySerializer(read_only=True)
    type = TypeSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False, allow_null=True)
    total_stock = serializers.SerializerMethodField()
    subproducts = SubProductSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)  # Aquí se incluyen los comentarios del producto

    class Meta:
        model = Product
        fields = '__all__'

    def get_total_stock(self, obj):
        """Calcula el stock total sumando el stock del producto y el de sus subproductos."""
        own_stock = Stock.objects.filter(product=obj, is_active=True).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        subproduct_stock = Stock.objects.filter(product__in=obj.subproducts.all(), is_active=True).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        return own_stock + subproduct_stock

    def validate(self, data):
        """Valida datos de nombre, código y restricciones para productos de categoría 'Cables'."""
        name = data.get('name', '')
        if not name:
            raise serializers.ValidationError({"name": "El nombre del producto no puede estar vacío."})

        # Verificación de categoría y tipo
        if not data.get('category') or not data.get('type'):
            raise serializers.ValidationError("El producto debe tener una categoría y un tipo.")

        # Verificación de código
        code = data.get('code', None)
        if code is not None:
            if not isinstance(code, int) or code <= 0:
                raise serializers.ValidationError({"code": "El código del producto debe ser un número entero positivo."})
            
            # Verificación de unicidad, mejorada para productos nuevos y existentes.
            if Product.objects.exclude(id=self.instance.id if self.instance else None).filter(code=code).exists():
                raise serializers.ValidationError({"code": "El código del producto ya está en uso."})

        # Validación para productos de la categoría 'Cables'
        category = self.instance.category if self.instance else data.get('category')
        if category and category.name.lower() == "cables":
            if not self.instance.subproducts.exists() and not self.instance.cable_attributes:
                raise serializers.ValidationError("Un producto de la categoría 'Cables' requiere subproductos o atributos de cable.")

        return data
