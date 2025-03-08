from rest_framework import serializers
from django.db.models import Sum

from apps.products.models.product_model import Product
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type

from apps.comments.models.comment_model import Comment
from apps.stocks.models.stock_model import Stock

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.api.serializers.category_serializer import CategorySerializer
from apps.products.api.serializers.type_serializer import TypeSerializer

from apps.comments.api.serializers.comment_serializer import CommentSerializer
from apps.stocks.api.serializers.stock_serializer import StockSerializer

class ProductSerializer(BaseSerializer):
    """Serializer para el producto con la lógica de validaciones y manejo de subproductos."""
    
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    type = serializers.PrimaryKeyRelatedField(queryset=Type.objects.all())
    total_stock = serializers.SerializerMethodField()
    subproducts = SubProductSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    # Añadimos modified_at y deleted_at como campos a representar
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'description', 'type', 'category', 
            'status', 'total_stock', 'image', 'comments', 'subproducts',
            'created_at', 'modified_at', 'deleted_at', 'created_by', 'modified_by', 'deleted_by'
        ]

    def get_total_stock(self, obj):
        """Calcula el stock total sumando el stock del producto y el de sus subproductos."""
        own_stock = obj.stocks.filter(is_active=True).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        subproduct_stock = Stock.objects.filter(product__in=obj.subproducts.all(), is_active=True).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        return own_stock + subproduct_stock

    def validate(self, data):
        """Valida datos de nombre, código y restricciones para productos de categoría 'Cables'."""
        name = data.get('name', '')
        if not name:
            raise serializers.ValidationError({"name": "El nombre del producto no puede estar vacío."})

        # Verificación de categoría y tipo
        if not data.get('category') or not data.get('type'):
            raise serializers.ValidationError("El producto debe tener una categoría y un tipo.")

        # Verificación de código
        code = data.get('code', None)
        if code is not None:
            if not isinstance(code, int) or code <= 0:
                raise serializers.ValidationError({"code": "El código del producto debe ser un número entero positivo."})
            
            # Verificación de unicidad, optimizada para productos nuevos y existentes.
            if self.instance is None:
                if Product.objects.filter(code=code).exists():
                    raise serializers.ValidationError({"code": "El código del producto ya está en uso."})
            else:  # Solo verificar unicidad si el producto está siendo actualizado y no hay cambios en el código.
                if Product.objects.exclude(id=self.instance.id).filter(code=code).exists():
                    raise serializers.ValidationError({"code": "El código del producto ya está en uso."})

        return data

    def to_representation(self, instance):
        """Ajusta la representación del objeto para asegurar valores correctos."""
        data = super().to_representation(instance)

        # Ajustamos los campos 'created_by', 'modified_by', 'deleted_by', 'created_at', 'modified_at', y 'deleted_at'
        data['created_at'] = instance.created_at
        data['modified_at'] = instance.modified_at if instance.modified_at else None  # Si no existe, devolverá None
        data['deleted_at'] = instance.deleted_at if instance.deleted_at else None  # Si no existe, devolverá None

        if instance.modified_by:
            data['modified_by'] = instance.modified_by.username
        else:
            data['modified_by'] = None

        if instance.deleted_by:
            data['deleted_by'] = instance.deleted_by.username
        else:
            data['deleted_by'] = None

        if instance.created_by:
            data['created_by'] = instance.created_by.username  # O el campo que prefieras mostrar

        return data
