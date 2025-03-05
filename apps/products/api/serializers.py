from rest_framework import serializers
from django.db.models import Sum
from apps.comments.api.serializers import CommentSerializer
from apps.stocks.models import Stock
from ..models import Category, Type, Product, CableAttributes


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'status']

    def validate_name(self, value):
        """✅ Valida que el nombre de la categoría no exista antes de crear o actualizar."""
        normalized_name = value.strip().lower()
        if self.instance:
            if Category.objects.exclude(id=self.instance.id).filter(name__iexact=normalized_name).exists():
                raise serializers.ValidationError("El nombre de la categoría ya existe. Debe ser único.")
        else:
            if Category.objects.filter(name__iexact=normalized_name).exists():
                raise serializers.ValidationError("El nombre de la categoría ya existe. Debe ser único.")
        return value


class TypeSerializer(serializers.ModelSerializer):
    """✅ Serializer para el tipo, incluyendo la categoría"""
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)

    class Meta:
        model = Type
        fields = ['id', 'name', 'description', 'category', 'status']

    def validate_name(self, value):
        """✅ Valida que no exista otro 'Type' con el mismo nombre"""
        normalized_name = value.strip().lower()
        if self.instance:
            if Type.objects.exclude(id=self.instance.id).filter(name__iexact=normalized_name).exists():
                raise serializers.ValidationError("El nombre del tipo ya existe. Debe ser único.")
        else:
            if Type.objects.filter(name__iexact=normalized_name).exists():
                raise serializers.ValidationError("El nombre del tipo ya existe. Debe ser único.")
        return value


class CableAttributesSerializer(serializers.ModelSerializer):
    """✅ Serializer para atributos específicos de productos de la categoría 'Cables'"""
    class Meta:
        model = CableAttributes
        fields = '__all__'
        extra_kwargs = {
            'status': {'required': False},
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
            'deleted_at': {'read_only': True}
        }


class NestedProductSerializer(serializers.ModelSerializer):
    """✅ Serializer para mostrar productos relacionados (subproductos)."""
    category = CategorySerializer(read_only=True)
    type = TypeSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'description', 'image', 'category',
            'type', 'created_at', 'modified_at', 'deleted_at', 'status', 'user'
        ]
        extra_kwargs = {
            'status': {'required': False},
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
            'deleted_at': {'read_only': True}
        }


class ProductSerializer(serializers.ModelSerializer):
    """✅ Serializer principal para productos."""
    category = CategorySerializer(read_only=True)
    type = TypeSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    subproducts = NestedProductSerializer(many=True, read_only=True)
    cable_attributes = CableAttributesSerializer(read_only=True)

    parent = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=False,
        allow_null=True
    )

    total_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        
    def get_total_stock(self, obj):
        """✅ Calcula el stock total del producto sumando su stock y el de sus subproductos."""
        own_stock = Stock.objects.filter(product=obj, is_active=True).aggregate(
            total_quantity=Sum('quantity')
        )['total_quantity'] or 0

        subproduct_stock = Stock.objects.filter(product__in=obj.subproducts.all(), is_active=True).aggregate(
            total_quantity=Sum('quantity')
        )['total_quantity'] or 0

        return own_stock + subproduct_stock

    def validate(self, data):
        """✅ Validaciones personalizadas para nombre, código y estructura de productos."""
        name = data.get('name', '').strip().lower().replace(" ", "")
        code = data.get('code', '').strip().lower().replace(" ", "")
        category = self.instance.category if self.instance else data.get('category')

        # Verificar si ya existe un producto con el mismo nombre o código
        existing_name = Product.objects.filter(name__iexact=name)
        existing_code = Product.objects.filter(code__iexact=code)

        if self.instance:  # Si es una actualización, excluirse a sí mismo
            existing_name = existing_name.exclude(id=self.instance.id)
            existing_code = existing_code.exclude(id=self.instance.id)

        if existing_name.exists():
            raise serializers.ValidationError({"name": "El nombre del producto ya existe. Debe ser único."})

        if existing_code.exists():
            raise serializers.ValidationError({"code": "El código del producto ya existe. Debe ser único."})

        # 🔥 Si el producto es de la categoría 'Cables', debe tener subproductos o atributos de cable
        if category and category.name.lower() == "cables":
            if not self.instance.subproducts.exists() and not self.instance.cable_attributes:
                raise serializers.ValidationError(
                    "Un producto de la categoría 'Cables' requiere subproductos o atributos de cable."
                )

        return data

    def validate_name(self, value):
        """✅ Normaliza el nombre antes de guardar"""
        return value.strip().lower().replace(" ", "")

    def validate_code(self, value):
        """✅ Normaliza el código antes de guardar"""
        return value.strip().lower().replace(" ", "")
