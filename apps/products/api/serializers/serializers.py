from rest_framework import serializers
from django.db.models import Sum
from apps.comments.api.serializers import CommentSerializer
from apps.stocks.models import Stock
from apps.products.models import Category, Type, Product, CableAttributes
from .base_serializer import BaseSerializer  # 🚀 Importamos la clase base

class CategorySerializer(BaseSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'status']

    def update(self, instance, validated_data):
        """
        Personaliza la actualización para registrar quién modificó la categoría.
        """
        request = self.context.get('request', None)
        if request and hasattr(request, "user"):
            validated_data['modified_by'] = request.user  # 🔥 Guarda el usuario que edita
        return super().update(instance, validated_data)
    
class TypeSerializer(BaseSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)

    class Meta:
        model = Type
        fields = ['id', 'name', 'description', 'category', 'status']

class CableAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CableAttributes
        fields = '__all__'
        extra_kwargs = {'status': {'required': False}}

class NestedProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    type = TypeSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'code', 'description', 'image', 'category', 'type', 'created_at', 'modified_at', 'deleted_at', 'status', 'user']

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
