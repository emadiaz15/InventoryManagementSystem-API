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
        """Valida que el nombre de la categoría no exista antes de crear o actualizar."""
        if self.instance:
            if Category.objects.exclude(id=self.instance.id).filter(name=value).exists():
                raise serializers.ValidationError("El nombre de la categoría ya existe. Debe ser único.")
        else:
            if Category.objects.filter(name=value).exists():
                raise serializers.ValidationError("El nombre de la categoría ya existe. Debe ser único.")
        return value


class TypeSerializer(serializers.ModelSerializer):
    """Serializer para el tipo, incluyendo la categoría"""
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)

    class Meta:
        model = Type
        fields = ['id', 'name', 'description', 'category', 'status']

    def validate_name(self, value):
        """Valida que no exista otro 'Type' con el mismo nombre"""
        if self.instance:
            if Type.objects.exclude(id=self.instance.id).filter(name=value).exists():
                raise serializers.ValidationError("El nombre del tipo ya existe. Debe ser único.")
        else:
            if Type.objects.filter(name=value).exists():
                raise serializers.ValidationError("El nombre del tipo ya existe. Debe ser único.")
        return value


class CableAttributesSerializer(serializers.ModelSerializer):
    """Serializer para atributos específicos de productos de la categoría 'Cables'"""
    class Meta:
        model = CableAttributes
        fields = [
            'id', 'brand', 'number_coil', 'initial_length',
            'total_weight', 'coil_weight', 'technical_sheet_photo',
            'created_at', 'modified_at', 'deleted_at', 'status'
        ]
        extra_kwargs = {
            'status': {'required': False},
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
            'deleted_at': {'read_only': True}
        }


class NestedProductSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar productos relacionados (subproductos).
    Solo lectura: No se espera crear/editar subproductos desde aquí.
    """
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
    """
    Serializer principal para productos, incluyendo:
      - subproductos (read_only)
      - atributos de cable (read_only)
      - comentarios (read_only)
      - posibilidad de asignar un 'parent' para productos que sean subproductos
      - total_stock (calculado en base a stock propio y subproductos)
    """
    # Relaciones de solo lectura
    category = CategorySerializer(read_only=True)
    type = TypeSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    subproducts = NestedProductSerializer(many=True, read_only=True)
    cable_attributes = CableAttributesSerializer(read_only=True)

    # Campo para asignar producto padre de forma opcional
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=False,
        allow_null=True
    )

    total_stock = serializers.SerializerMethodField()  # <-- Asegúrate de definir esto correctamente

    class Meta:
        model = Product
        fields = '__all__'

    def get_total_stock(self, obj):
        """
        Calcula el stock total de un producto:
        - Si tiene subproductos, suma el stock de los subproductos.
        - Si no tiene subproductos, usa su propio stock.
        """
        own_stock = Stock.objects.filter(product=obj, is_active=True).aggregate(
            total_quantity=Sum('quantity')
        )['total_quantity'] or 0

        subproduct_stock = Stock.objects.filter(product__in=obj.subproducts.all(), is_active=True).aggregate(
            total_quantity=Sum('quantity')
        )['total_quantity'] or 0

        return own_stock + subproduct_stock


    def validate(self, data):
        """
        Validaciones personalizadas para asegurar consistencia en productos y subproductos.
        """
        category = self.instance.category if self.instance else data.get('category')
        if category and category.name == "Cables":
            # Si el producto pertenece a la categoría 'Cables' y no tiene subproductos,
            # debe tener atributos de cable.
            if not self.instance.subproducts.exists() and not self.instance.cable_attributes:
                raise serializers.ValidationError(
                    "Un producto de categoría 'Cables' requiere subproductos o atributos de cable."
                )

        return data
