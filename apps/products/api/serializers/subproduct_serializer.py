from rest_framework import serializers
from django.db.models import Sum

from apps.stocks.models import Stock
from apps.products.models.subproduct_model import Subproduct

from apps.stocks.api.serializers import StockSerializer
from apps.comments.api.serializers import CommentSerializer
from apps.products.api.serializers.base_serializer import BaseSerializer

class SubProductSerializer(BaseSerializer):
    """Serializer para subproductos con la lógica de stock y atributos de cable."""

    stock_quantity = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    number_coil = serializers.SerializerMethodField()
    initial_length = serializers.SerializerMethodField()
    final_length = serializers.SerializerMethodField()
    total_weight = serializers.SerializerMethodField()
    coil_weight = serializers.SerializerMethodField()
    technical_sheet_photo = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True)  # Añadir comentarios

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
        """Obtiene un atributo específico de Subproduct."""
        try:
            subproduct = obj.cable_subproduct  # Asegúrate de que la relación es correcta
            return getattr(subproduct, attribute, None) if subproduct else None
        except Subproduct.DoesNotExist:
            return None
