from rest_framework import serializers
from apps.comments.api.serializers import CommentSerializer
from ..models import Category, Type, Product, CableAttributes


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'status']

    def validate_name(self, value):
        """Valida que el nombre de la categoría no exista"""
        if Category.objects.filter(name=value).exists():
            raise serializers.ValidationError("El nombre de la categoría ya existe. Debe ser único.")
        return value

    def update(self, instance, validated_data):
        """Verifica que el nuevo nombre no exista antes de actualizar"""
        new_name = validated_data.get('name', instance.name)
        if new_name != instance.name and Category.objects.filter(name=new_name).exists():
            raise serializers.ValidationError("El nombre de la categoría ya existe. Debe ser único.")
        
        instance.name = new_name
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class TypeSerializer(serializers.ModelSerializer):
    """Serializer para el tipo, incluyendo la categoría"""
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)

    class Meta:
        model = Type
        fields = ['id', 'name', 'description', 'category', 'status']

    def get_category(self, obj):
        """Devuelve el ID y el nombre de la categoría asociada"""
        return {"id": obj.category.id, "name": obj.category.name} if obj.category else None
    
    def validate_name(self, value):
        """Valida que no exista otro 'Type' con el mismo nombre"""
        if Type.objects.filter(name=value).exists():
            raise serializers.ValidationError("El nombre del tipo ya existe. Debe ser único.")
        return value

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
    """
    Serializer para mostrar productos relacionados (subproductos).
    Sólo lectura: no se espera crear/editar subproductos desde aquí.
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
        Validación personalizada (Enfoque Mixto):
        - Se elimina la restricción que impedía coexistir CableAttributes y subproductos.
        - Puedes agregar lógica adicional si lo deseas.
        """
        # Ejemplo: si deseas forzar que, si es categoría 'Cables' y no tiene subproductos,
        # debe tener CableAttributes. (Descomenta y adapta a tu preferencia)
        #
        # category = self.instance.category if self.instance else data.get('category')
        # if category and category.name == "Cables":
        #     # Si no hay subproductos y tampoco hay CableAttributes, error
        #     if not self.instance.subproducts.exists() and not self.instance.cable_attributes:
        #         raise serializers.ValidationError(
        #             "Un producto de categoría 'Cables' requiere subproductos o CableAttributes."
        #         )

        return data
