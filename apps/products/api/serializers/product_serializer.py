from rest_framework import serializers
from django.db.models import Sum
from apps.stocks.models import Stock
from apps.comments.api.serializers import CommentSerializer
from apps.products.models import Product
from .base_serializer import BaseSerializer
from apps.products.api.serializers.nested_product_serializer import NestedProductSerializer
from apps.stocks.api.serializers import StockSerializer
from apps.products.api.serializers.cable_attributes_serializer import CableAttributesSerializer
from apps.products.api.serializers.type_serializer import TypeSerializer
from apps.products.api.serializers.category_serializer import CategorySerializer

class ProductSerializer(BaseSerializer):
    category = CategorySerializer(read_only=True)
    type = TypeSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    subproducts = NestedProductSerializer(many=True, read_only=True)
    cable_attributes = CableAttributesSerializer(read_only=True)

    parent = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False, allow_null=True)
    total_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_total_stock(self, obj):
        """✅ Calcula el stock total sumando su stock y el de sus subproductos."""
        own_stock = Stock.objects.filter(product=obj, is_active=True).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        subproduct_stock = Stock.objects.filter(product__in=obj.subproducts.all(), is_active=True).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        return own_stock + subproduct_stock

    def validate(self, data):
        """✅ Validaciones de nombre, código y restricciones de productos 'Cables'."""
        name = self._normalize_field(data.get('name', ''))
        code = self._normalize_field(str(data.get('code', '')))  # 🔥 Aseguramos que code sea string

        # Verificar si ya existe un producto con el mismo nombre o código
        existing_name = Product.objects.exclude(id=self.instance.id if self.instance else None).filter(name__iexact=name)
        existing_code = Product.objects.exclude(id=self.instance.id if self.instance else None).filter(code__iexact=code)

        if existing_name.exists():
            raise serializers.ValidationError({"name": "El nombre del producto ya existe. Debe ser único."})

        if existing_code.exists():
            raise serializers.ValidationError({"code": "El código del producto ya existe. Debe ser único."})

        # 🔥 Si el producto es de la categoría 'Cables', debe tener subproductos o atributos de cable
        category = self.instance.category if self.instance else data.get('category')
        if category and category.name.lower() == "cables":
            if not self.instance.subproducts.exists() and not self.instance.cable_attributes:
                raise serializers.ValidationError("Un producto de la categoría 'Cables' requiere subproductos o atributos de cable.")

        data['name'] = name  # Guardamos el nombre normalizado
        data['code'] = code  # Guardamos el código normalizado
        return data
