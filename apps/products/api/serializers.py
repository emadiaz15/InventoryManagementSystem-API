from rest_framework import serializers
from ..models import Category, Type, Product, CableAttributes
from apps.comments.api.serializers import CommentSerializer

class CategorySerializer(serializers.ModelSerializer):
    # Serializer para la categoría con campos básicos
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'status']


class TypeSerializer(serializers.ModelSerializer):
    # Serializer para el tipo, incluyendo la categoría a la que pertenece
    class Meta:
        model = Type
        fields = ['id', 'name', 'description', 'category', 'status']


class CableAttributesSerializer(serializers.ModelSerializer):
    # Serializer para los atributos específicos de productos de la categoría 'Cables'
    class Meta:
        model = CableAttributes
        fields = [
            'id', 'name', 'brand', 'number_coil', 'initial_length',
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
    # Serializer para mostrar subproductos (productos hijo) sin recursión infinita
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
    # Serializer principal para el producto
    # Incluye categorías, tipos, usuario y comentarios de solo lectura
    category = CategorySerializer(read_only=True)
    type = TypeSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    subproducts = NestedProductSerializer(many=True, read_only=True)  # Subproductos de solo lectura
    cable_attributes = CableAttributesSerializer(read_only=True)      # Atributos de cable si aplica

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
        # Si el producto pertenece a la categoría 'Cables', en actualización se requiere al menos un subproducto activo.
        category = self.instance.category if self.instance else data.get('category')

        # Verifica si la categoría es 'Cables'
        if category and category.name == "Cables":
            # Si es actualización (self.instance existe), revisa los subproductos existentes
            if self.instance:
                has_active_subproducts = self.instance.subproducts.filter(status=True).exists()
                if not has_active_subproducts:
                    # Mensaje de error en inglés
                    raise serializers.ValidationError("At least one active subproduct is required for 'Cables' category products.")
        
        return data
