from rest_framework import serializers
from ..models import Category, Type, Product, CableAttributes
from apps.comments.api.serializers import CommentSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer para la categoría con campos básicos"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'status']


class TypeSerializer(serializers.ModelSerializer):
    """Serializer para el tipo, incluyendo la categoría a la que pertenece"""
    class Meta:
        model = Type
        fields = ['id', 'name', 'description', 'category', 'status']


class CableAttributesSerializer(serializers.ModelSerializer):
    """Serializer para los atributos específicos de productos de la categoría 'Cables'"""
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
    """Serializer para mostrar productos relacionados (subproductos)"""
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
    Serializer principal para productos, incluyendo subproductos y atributos de cable
    """
    category = CategorySerializer(read_only=True)
    type = TypeSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    subproducts = NestedProductSerializer(many=True, read_only=True)  # Subproductos
    cable_attributes = CableAttributesSerializer(read_only=True)  # Atributos de cable si aplica

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'status': {'required': False},
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
            'deleted_at': {'read_only': True}
        }

    def validate(self, data):
        """
        Validación personalizada:
        - Requiere al menos un subproducto activo si el producto pertenece a la categoría 'Cables'.
        - Verifica que un producto con subproductos no pueda tener atributos de cable.
        """
        category = self.instance.category if self.instance else data.get('category')

        # Validación para la categoría 'Cables'
        if category and category.name == "Cables":
            # Verifica que el producto tenga al menos un subproducto activo
            if self.instance and not self.instance.subproducts.filter(status=True).exists():
                raise serializers.ValidationError(
                    "El producto de categoría 'Cables' debe tener al menos un subproducto activo."
                )

            # Un producto con subproductos no puede tener CableAttributes
            if self.instance and self.instance.cable_attributes:
                raise serializers.ValidationError(
                    "Un producto con subproductos no puede tener atributos de cable (CableAttributes)."
                )

        # Validación adicional: un producto con atributos de cable no puede ser un subproducto
        if data.get('parent') and self.instance and self.instance.cable_attributes:
            raise serializers.ValidationError(
                "Un producto con atributos de cable no puede ser un subproducto."
            )

        return data
