from rest_framework import serializers
from django.db.models import Sum
from apps.stocks.models import Stock
from apps.products.models import Category, Type, Product
from apps.comments.api.serializers import CommentSerializer
from .base_serializer import BaseSerializer
from apps.products.api.serializers.nested_product_serializer import NestedProductSerializer
from apps.products.api.serializers.cable_attributes_serializer import CableAttributesSerializer
from apps.products.api.serializers.type_serializer import TypeSerializer
from apps.products.api.serializers.category_serializer import CategorySerializer
from apps.comments.models import Comment
from apps.comments.api.serializers import CommentSerializer
from django.contrib.contenttypes.models import ContentType

class ProductSerializer(serializers.ModelSerializer):
    """Serializer para el producto con lógica de validaciones y manejo de subproductos."""
    
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)  # Cambié a required=False
    type = serializers.PrimaryKeyRelatedField(queryset=Type.objects.all(), required=False)  # Cambié a required=False
    user = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    cable_attributes = CableAttributesSerializer(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False, allow_null=True)
    total_stock = serializers.SerializerMethodField()
    subproducts = NestedProductSerializer(many=True, read_only=True)
    
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
        
        if not data.get('category') or not data.get('type'):
            raise serializers.ValidationError("El producto debe tener una categoría y un tipo.")

        code = data.get('code', None)
        if code is not None:
            if not isinstance(code, int) or code <= 0:
                raise serializers.ValidationError({"code": "El código del producto debe ser un número entero positivo."})
            
            # Verificación de unicidad, mejorada para productos nuevos y existentes.
            if Product.objects.exclude(id=self.instance.id if self.instance else None).filter(code=code).exists():
                raise serializers.ValidationError({"code": "El código del producto ya está en uso."})


        # Validación específica para productos en la categoría 'Cables'
        category = self.instance.category if self.instance else data.get('category')
        if category and category.name.lower() == "cables":
            if not self.instance.subproducts.exists() and not self.instance.cable_attributes:
                raise serializers.ValidationError("Un producto de la categoría 'Cables' requiere subproductos o atributos de cable.")

        return data
    def get_subproducts(self, obj):
        """Método para devolver los subproductos en el formato deseado"""
        subproducts = obj.subproducts.filter(status=True)  # Solo subproductos activos
        return [
            {
                "id": sub.id,
                "name": sub.name,
                "description": sub.description,
                "status": sub.status,
                "created_at": sub.created_at.isoformat() if sub.created_at else None,
                "modified_at": sub.modified_at.isoformat() if sub.modified_at else None,
                "stock_quantity": sub.stock_quantity,
                "brand": sub.brand,
                "number_coil": sub.number_coil,
                "initial_length": sub.initial_length,
                "final_length": sub.final_length,
                "total_weight": sub.total_weight,
                "coil_weight": sub.coil_weight,
                "technical_sheet_photo": sub.technical_sheet_photo.url if sub.technical_sheet_photo else None,
                "created_by": sub.created_by.id,
                "modified_by": sub.modified_by.id if sub.modified_by else None,
                "deleted_by": sub.deleted_by.id if sub.deleted_by else None,
                "comments": CommentSerializer(Comment.active_objects.filter(content_type=ContentType.objects.get_for_model(Product), object_id=sub.id), many=True).data
            }
            for sub in subproducts
        ]
