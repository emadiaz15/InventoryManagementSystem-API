from rest_framework import serializers
from django.db.models import Sum
from apps.stocks.models import SubproductStock
from apps.products.models.subproduct_model import Subproduct
from apps.comments.api.serializers.comment_subproduct import SubproductCommentSerializer
from apps.products.api.serializers.base_serializer import BaseSerializer

class SubProductSerializer(BaseSerializer):
    """Serializer para subproductos con lógica de stock y atributos de cable."""
    
    name = serializers.CharField(max_length=200, default="unnamed")
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    status = serializers.BooleanField(default=True)
    stock_quantity = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    number_coil = serializers.SerializerMethodField()
    initial_length = serializers.SerializerMethodField()
    final_length = serializers.SerializerMethodField()
    total_weight = serializers.SerializerMethodField()
    coil_weight = serializers.SerializerMethodField()
    technical_sheet_photo = serializers.SerializerMethodField()
    comments = SubproductCommentSerializer(many=True, required=False)

    class Meta:
        model = Subproduct
        fields = [
            'id', 'name', 'description', 'status', 'created_at', 'modified_at', 'stock_quantity',
            'brand', 'number_coil', 'initial_length', 'final_length', 'total_weight', 'coil_weight',
            'technical_sheet_photo', 'created_by', 'modified_by', 'deleted_by', 'comments'
        ]

    def get_stock_quantity(self, obj):
        """Devuelve la cantidad total de stock del subproducto."""
        # Prefetching stock en la vista o en el método `to_representation`
        stock = SubproductStock.objects.filter(subproduct=obj, status=True).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        return stock

    def get_brand(self, obj):
        return self._get_subproduct_attribute(obj, 'brand')

    def get_number_coil(self, obj):
        return self._get_subproduct_attribute(obj, 'number_coil')

    def get_initial_length(self, obj):
        return self._get_subproduct_attribute(obj, 'initial_length')

    def get_final_length(self, obj):
        return self._get_subproduct_attribute(obj, 'final_length')

    def get_total_weight(self, obj):
        return self._get_subproduct_attribute(obj, 'total_weight')

    def get_coil_weight(self, obj):
        return self._get_subproduct_attribute(obj, 'coil_weight')

    def get_technical_sheet_photo(self, obj):
        """Devuelve la foto de la hoja técnica del subproducto."""
        return self._get_subproduct_attribute(obj, 'technical_sheet_photo')

    def _get_subproduct_attribute(self, obj, attribute):
        """Obtiene un atributo específico del subproducto, asegurando que si no existe, devuelva None."""
        return getattr(obj, attribute, None)

    def to_representation(self, instance):
        """Sobrescribe la representación para mejorar la eficiencia de las consultas."""
        # Prefetch de comentarios, stock y otros atributos
        comments = instance.comments.all()
        
        # Agregamos el stock_quantity usando `prefetch_related` en la vista
        stock_quantity = SubproductStock.objects.filter(subproduct=instance, status=True).aggregate(
            total_quantity=Sum('quantity'))['total_quantity'] or 0
        
        # Realizamos la representación estándar
        representation = super().to_representation(instance)
        
        # Agregamos el stock_quantity y los comentarios prefetch
        representation['stock_quantity'] = stock_quantity
        representation['comments'] = SubproductCommentSerializer(comments, many=True).data
        
        return representation
