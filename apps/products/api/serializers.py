from rest_framework import serializers
from ..models import Category, Type, Product, SubProduct
from apps.comments.api.serializers import CommentSerializer

# Serializer para Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'status']


# Serializer para Type
class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ['id', 'name', 'description', 'category', 'status']


# Serializer para SubProduct
class SubProductSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = SubProduct
        fields = [
            'id', 'product', 'name', 'brand', 'number_coil', 'initial_length', 
            'total_weight', 'coil_weight', 'technical_sheet_photo', 
            'created_at', 'modified_at', 'deleted_at', 'is_active', 'comments'
        ]
        extra_kwargs = {
            'is_active': {'required': False}
        }


# Serializer para Product con relaciones
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    type = TypeSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    subproducts = SubProductSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'is_active': {'required': False}
        }

    def validate(self, data):
        """
        Si el producto es de la categoría "Cables", verifica que tenga al menos un subproducto
        con los campos requeridos.
        """
        category = data.get('category')
        if category and category.name == "Cables":
            if not data.get('subproducts'):
                raise serializers.ValidationError("Se requiere al menos un subproducto para productos de tipo 'Cables'.")
            
            for subproduct in data.get('subproducts'):
                required_fields = ['brand', 'number_coil', 'initial_length', 'total_weight', 'coil_weight', 'technical_sheet_photo']
                missing_fields = [field for field in required_fields if not getattr(subproduct, field)]
                
                if missing_fields:
                    raise serializers.ValidationError(
                        f"Faltan los siguientes campos en los subproductos: {', '.join(missing_fields)}"
                    )
        return data
