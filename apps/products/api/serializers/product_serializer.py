from rest_framework import serializers
from decimal import Decimal

from apps.products.models.product_model import Product
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type

from apps.products.api.serializers.subproduct_serializer import SubProductSerializer

from .base_serializer import BaseSerializer 

class ProductSerializer(BaseSerializer):
    """
    Serializer final para Producto.
    - Usa BaseSerializer para auditoría.
    - Muestra stock actual calculado ('current_stock').
    - Acepta opcionalmente ajuste de stock en PUT ('quantity_change', 'reason').
    """

    # --- Campos de Relación ---
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(status=True), # Filtra por activos
        required=True
    )
    type = serializers.PrimaryKeyRelatedField(
        queryset=Type.objects.filter(status=True), # Filtra por activos
        required=True
    )
    # Campos para mostrar nombres en GET (read-only)
    category_name = serializers.CharField(source='category.name', read_only=True)
    type_name = serializers.CharField(source='type.name', read_only=True)

    # --- Relación Anidada (Solo Lectura) ---
    subproducts = SubProductSerializer(many=True, read_only=True)

    # --- Campo Calculado de Stock (Solo Lectura) ---
    # Este campo se llena mediante anotaciones en las vistas GET
    current_stock = serializers.DecimalField(
        max_digits=15, decimal_places=2, # Ajusta según tus modelos de stock
        read_only=True,
        default=Decimal('0.00') # Valor por defecto
    )

    # --- Campos para AJUSTE DE STOCK en PUT (Solo Escritura) ---
    quantity_change = serializers.DecimalField(
        max_digits=15, decimal_places=2,
        write_only=True, # No se muestra en la respuesta
        required=False, # Es opcional en el PUT
        allow_null=True # Permitir que no se envíe
    )
    reason = serializers.CharField(
        max_length=255,
        write_only=True, # No se muestra en la respuesta
        required=False, # Es opcional en el PUT
        allow_null=True,
        allow_blank=True # Permitir razón vacía si se envía
    )
    class Meta:
        model = Product
        # Listamos todos los campos relevantes para la API
        fields = [
            'id', 'name', 'code', 'description', 'brand', 'image', # Campos modelo
            'category', 'type', # FKs (IDs)
            'category_name', 'type_name', # Representación FKs
            'has_individual_stock', # Flag de control
            'current_stock', # Stock actual (calculado en GET)
            'subproducts', # Lista anidada read-only
            'status', # El status booleano heredado (activo/inactivo)
            'created_at', 'modified_at', 'deleted_at', # Timestamps heredados
            # Campos de representación de usuarios (formateados por BaseSerializer)
            'created_by', 'modified_by', 'deleted_by',
            # Campos write_only (no aparecerán en respuesta, pero son aceptados en PUT)
            'quantity_change', 'reason',
        ]
        # Campos que son solo para mostrar o asignados automáticamente por el backend
        read_only_fields = [
            'status', 'has_individual_stock', 'subproducts', 'current_stock',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by',
            'category_name', 'type_name',
        ]

    # --- Validaciones Específicas ---
    def validate_name(self, value):
        """Aplica la validación de nombre único normalizado heredada."""
        if value: return self._get_normalized_name(value)
        return value

    def validate_code(self, value):
        """Aplica la validación de código único heredada."""
        if value is not None: self._validate_unique_code(value)
        return value

    def validate_quantity_change(self, value):
        """Valida la cantidad de ajuste si se proporciona."""
        if value is not None and value == 0:
            raise serializers.ValidationError("La cantidad del ajuste no puede ser cero si se proporciona.")
        return value

    def validate(self, data):
        """Validar que 'reason' exista si 'quantity_change' existe."""
        quantity_change = data.get('quantity_change')
        reason = data.get('reason')

        # Si se intenta ajustar stock (quantity_change no es None y no es 0), se requiere razón
        if quantity_change is not None and quantity_change != 0 and not reason:
             raise serializers.ValidationError({"reason": "Se requiere una razón para el ajuste de stock."})
        # Opcional: requerir cantidad si se da una razón
        # if reason and quantity_change is None:
        #      raise serializers.ValidationError({"quantity_change": "Se requiere una cantidad para el ajuste con esta razón."})

        return data
