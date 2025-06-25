from rest_framework import serializers
from decimal import Decimal

from apps.products.models.product_model import Product
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.api.serializers.product_image_serializer import ProductImageSerializer

from .base_serializer import BaseSerializer


class ProductSerializer(BaseSerializer):
    """
    Serializer final para Producto.
    - Usa BaseSerializer para auditoría.
    - Muestra stock actual calculado ('current_stock').
    - Incluye imágenes relacionadas ('product_images').
    - Acepta ajuste de stock opcional en PUT ('quantity_change', 'reason').
    """

    # --- Relaciones ---
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(status=True),
        required=True
    )

    type = serializers.PrimaryKeyRelatedField(
        queryset=Type.objects.filter(status=True),
        required=False,
        allow_null=True
    )

    # --- Derivados de FK ---
    category_name = serializers.CharField(source='category.name', read_only=True)
    type_name = serializers.CharField(source='type.name', read_only=True)

    # --- Subproductos e imágenes ---
    subproducts = SubProductSerializer(many=True, read_only=True)
    product_images = ProductImageSerializer(many=True, read_only=True)

    # --- Stock actual dinámico ---
    current_stock = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True,
        default=Decimal("0.00")
    )

    # --- Ajuste opcional de stock (escritura solamente) ---
    quantity_change = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        write_only=True,
        required=False,
        allow_null=True
    )
    reason = serializers.CharField(
        max_length=255,
        write_only=True,
        required=False,
        allow_null=True,
        allow_blank=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'description', 'brand', 'location',
            'category', 'type', 'position',
            'category_name', 'type_name',
            'has_subproducts',
            'current_stock',
            'subproducts',
            'product_images',
            'status',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by',
            'quantity_change', 'reason',
        ]
        read_only_fields = [
            'status', 'subproducts', 'current_stock', 'product_images',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by',
            'category_name', 'type_name',
        ]

    # --- Validaciones personalizadas ---
    def validate_name(self, value):
        return self._get_normalized_name(value) if value else value

    def validate_code(self, value):
        qs = Product.objects.filter(code=value, status=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un producto con este código.")
        return value

    def validate_quantity_change(self, value):
        if value is not None and value == 0:
            raise serializers.ValidationError("La cantidad del ajuste no puede ser cero.")
        return value

    def validate(self, data):
        quantity_change = data.get("quantity_change")
        reason = data.get("reason")
        if quantity_change and not reason:
            raise serializers.ValidationError({"reason": "Se requiere una razón para el ajuste de stock."})
        return data

        # --- Representación personalizada para el frontend ---
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Solo forzar type/category IDs si querés, pero NO sobrescribas name
        rep["type"] = instance.type.id if instance.type else None
        rep["category"] = instance.category.id if instance.category else None

        return rep
