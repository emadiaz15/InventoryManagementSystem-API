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
    # Relación con comentarios en modo de solo lectura
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = SubProduct
        fields = [
            'id', 'product', 'name', 'brand', 'number_coil', 'initial_length', 
            'total_weight', 'coil_weight', 'technical_sheet_photo', 
            'created_at', 'modified_at', 'deleted_at', 'is_active', 'comments'
        ]
        extra_kwargs = {
            'is_active': {'required': False},
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
            'deleted_at': {'read_only': True}
        }


# Serializer para Product con relaciones
class ProductSerializer(serializers.ModelSerializer):
    # Relación de solo lectura con Category y Type
    category = CategorySerializer(read_only=True)
    type = TypeSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)  # Relación de usuario como cadena
    comments = CommentSerializer(many=True, read_only=True)  # Comentarios de solo lectura
    subproducts = SubProductSerializer(many=True, read_only=True)  # Subproductos de solo lectura

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'is_active': {'required': False},
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
            'deleted_at': {'read_only': True}
        }

    def validate(self, data):
        """
        Si el producto es de la categoría "Cables", verifica que tenga al menos un subproducto activo.
        """
        # Verifica si el producto pertenece a la categoría "Cables"
        category = self.instance.category if self.instance else data.get('category')
        if category and category.name == "Cables":
            # Si es una actualización, verifica si hay subproductos activos
            if self.instance:
                has_active_subproducts = self.instance.subproducts.filter(is_active=True).exists()
                if not has_active_subproducts:
                    raise serializers.ValidationError("Se requiere al menos un subproducto activo para productos de la categoría 'Cables'.")
            else:
                # En una creación, verifica que se incluya al menos un subproducto
                if not data.get('subproducts'):
                    raise serializers.ValidationError("Se requiere al menos un subproducto para productos de la categoría 'Cables'.")
        
        return data
