from rest_framework import serializers
from django.conf import settings
from apps.stocks.models.stock_event_model import StockEvent
from apps.stocks.models.stock_product_model import ProductStock
from apps.stocks.models.stock_subproduct_model import SubproductStock
from apps.products.api.serializers.base_serializer import BaseSerializer

class StockEventSerializer(BaseSerializer):
    """Serializer para eventos de stock, usando BaseSerializer para auditoría."""

    # --- Campos de Relación (Escribibles en la creación via servicio/repo) ---
    product_stock = serializers.PrimaryKeyRelatedField(
        queryset=ProductStock.objects.all(),
        required=False, # Solo uno de los dos es requerido
        allow_null=True
    )
    subproduct_stock = serializers.PrimaryKeyRelatedField(
        queryset=SubproductStock.objects.all(),
        required=False, # Solo uno de los dos es requerido
        allow_null=True
    )

    # --- Campos de Representación (Solo Lectura) ---
    # Mostramos info del stock afectado y del usuario creador
    product_stock_info = serializers.StringRelatedField(source='product_stock', read_only=True)
    subproduct_stock_info = serializers.StringRelatedField(source='subproduct_stock', read_only=True)

    class Meta:
        model = StockEvent
        fields = [
            'id',
            # Campos específicos del evento
            'quantity_change', 'event_type', 'location', 'notes',
            # FKs (solo IDs para posible entrada, representación arriba)
            'product_stock', 'subproduct_stock',
            # Campos de representación
            'product_stock_info', 'subproduct_stock_info',
            # Campos de auditoría (heredados y formateados por BaseSerializer)
            'created_at', # modified_at/deleted_at/status no son relevantes para Evento
            'created_by', # Clave final formateada por to_representation
        ]
        # Campos que son solo para mostrar o asignados automáticamente
        read_only_fields = [
            'created_at',
            'created_by_username', # Campo interno de BaseSerializer
            'product_stock_info', 'subproduct_stock_info',
        ]

    def validate(self, data):
        """Asegura que el evento esté ligado a un stock y el cambio no sea cero."""
        product_stock = data.get('product_stock', getattr(self.instance, 'product_stock', None))
        subproduct_stock = data.get('subproduct_stock', getattr(self.instance, 'subproduct_stock', None))
        quantity_change = data.get('quantity_change', getattr(self.instance, 'quantity_change', 0))

        if not product_stock and not subproduct_stock:
            raise serializers.ValidationError("El evento debe asociarse a un ProductStock o a un SubproductStock.")
        if product_stock and subproduct_stock:
            raise serializers.ValidationError("El evento no puede asociarse a un ProductStock y a un SubproductStock a la vez.")
        if quantity_change == 0:
            raise serializers.ValidationError("La cantidad de cambio no puede ser cero.")

        return data
