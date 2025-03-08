from rest_framework import serializers
from django.db.models import Sum

from apps.stocks.models.stock_model import Stock
from apps.products.models.subproduct_model import Subproduct

from apps.stocks.api.serializers.stock_serializer import StockSerializer
from apps.comments.api.serializers.comment_serializer import CommentSerializer
from apps.products.api.serializers.base_serializer import BaseSerializer

class SubProductSerializer(BaseSerializer):
    """Serializer para subproductos con la lógica de stock y atributos de cable."""
    name=serializers.CharField(max_length=200,default="unnamed")
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    status=serializers.BooleanField(default=True)
    stock_quantity = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    number_coil = serializers.SerializerMethodField()
    initial_length = serializers.SerializerMethodField()
    final_length = serializers.SerializerMethodField()
    total_weight = serializers.SerializerMethodField()
    coil_weight = serializers.SerializerMethodField()
    technical_sheet_photo = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, required=False)  # Añadir comentarios

    class Meta:
        model = Subproduct  # Asegúrate de que es Subproduct, no Product
        fields = [
            'id', 'name', 'description', 'status', 'created_at', 'modified_at', 'stock_quantity', 
            'brand', 'number_coil', 'initial_length', 'final_length', 'total_weight', 'coil_weight', 
            'technical_sheet_photo', 'created_by', 'modified_by', 'deleted_by', 'comments'
        ]

    def get_stock_quantity(self, obj):
        """Devuelve la cantidad de stock del subproducto."""
        stock = Stock.objects.filter(product=obj, is_active=True).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        return stock

    def get_brand(self, obj):
        """Devuelve la marca del subproducto."""
        return self._get_subproduct_attribute(obj, 'brand')

    def get_number_coil(self, obj):
        """Devuelve el número de bobinas del subproducto."""
        return self._get_subproduct_attribute(obj, 'number_coil')

    def get_initial_length(self, obj):
        """Devuelve la longitud inicial del subproducto."""
        return self._get_subproduct_attribute(obj, 'initial_length')

    def get_final_length(self, obj):
        """Devuelve la longitud final del subproducto."""
        return self._get_subproduct_attribute(obj, 'final_length')

    def get_total_weight(self, obj):
        """Devuelve el peso total del subproducto."""
        return self._get_subproduct_attribute(obj, 'total_weight')

    def get_coil_weight(self, obj):
        """Devuelve el peso de la bobina del subproducto."""
        return self._get_subproduct_attribute(obj, 'coil_weight')

    def get_technical_sheet_photo(self, obj):
        """Devuelve la foto de la hoja técnica del subproducto."""
        technical_sheet_photo = self._get_subproduct_attribute(obj, 'technical_sheet_photo')
        return technical_sheet_photo.url if technical_sheet_photo else None

    def _get_subproduct_attribute(self, obj, attribute):
        """Obtiene un atributo específico del subproducto.

        Si el atributo es un campo relacionado, accede a él y devuelve el valor.
        Si el atributo es nulo o no existe, devuelve None.
        """
        try:
            # Si el atributo es una relación, intenta obtener el campo relacionado
            value = getattr(obj, attribute, None)
            if value and hasattr(value, 'url'):  # Si es un archivo, devuelve la URL
                return value
            return value
        except AttributeError:
            return None
