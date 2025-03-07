from rest_framework import serializers
from apps.stocks.models import Stock
from apps.products.models import Product, CableAttributes
from django.db.models import Sum
from apps.products.api.serializers.cable_attributes_serializer import CableAttributesSerializer
from apps.stocks.api.serializers import StockSerializer

class NestedProductSerializer(serializers.ModelSerializer):
    """Serializer para subproductos"""

    stock_quantity = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    number_coil = serializers.SerializerMethodField()
    initial_length = serializers.SerializerMethodField()
    final_length = serializers.SerializerMethodField()
    total_weight = serializers.SerializerMethodField()
    coil_weight = serializers.SerializerMethodField()
    technical_sheet_photo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        # Aseguramos de no excluir campos que no están en el modelo
        exclude = ['category', 'type', 'code']  # Solo los campos que existen en el modelo

    def get_stock_quantity(self, obj):
        """Devuelve la cantidad de stock del subproducto"""
        stock = Stock.objects.filter(product=obj, is_active=True).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        return stock

    def get_brand(self, obj):
        """Devuelve la marca del subproducto"""
        try:
            cable_attributes = obj.cable_subproduct  # Intentamos acceder al atributo OneToOne
            return cable_attributes.brand if cable_attributes else None
        except CableAttributes.DoesNotExist:
            return None

    def get_number_coil(self, obj):
        """Devuelve el número de bobinas del subproducto"""
        try:
            cable_attributes = obj.cable_subproduct
            return cable_attributes.number_coil if cable_attributes else None
        except CableAttributes.DoesNotExist:
            return None

    def get_initial_length(self, obj):
        """Devuelve la longitud inicial del subproducto"""
        try:
            cable_attributes = obj.cable_subproduct
            return cable_attributes.initial_length if cable_attributes else None
        except CableAttributes.DoesNotExist:
            return None

    def get_final_length(self, obj):
        """Devuelve la longitud final del subproducto"""
        try:
            cable_attributes = obj.cable_subproduct
            return cable_attributes.final_length if cable_attributes else None
        except CableAttributes.DoesNotExist:
            return None

    def get_total_weight(self, obj):
        """Devuelve el peso total del subproducto"""
        try:
            cable_attributes = obj.cable_subproduct
            return cable_attributes.total_weight if cable_attributes else None
        except CableAttributes.DoesNotExist:
            return None

    def get_coil_weight(self, obj):
        """Devuelve el peso de la bobina del subproducto"""
        try:
            cable_attributes = obj.cable_subproduct
            return cable_attributes.coil_weight if cable_attributes else None
        except CableAttributes.DoesNotExist:
            return None

    def get_technical_sheet_photo(self, obj):
        """Devuelve la foto de la hoja técnica del subproducto"""
        try:
            cable_attributes = obj.cable_subproduct
            return cable_attributes.technical_sheet_photo.url if cable_attributes and cable_attributes.technical_sheet_photo else None
        except CableAttributes.DoesNotExist:
            return None
