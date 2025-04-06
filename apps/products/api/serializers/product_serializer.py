from rest_framework import serializers
from apps.products.models.product_model import Product
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from .base_serializer import BaseSerializer

class ProductSerializer(BaseSerializer): # Correcto: hereda de BaseSerializer
    """Serializer para Producto, usando BaseSerializer para auditoría."""

    # Define cómo manejar FKs en la entrada/salida
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=True # Producto debe tener categoría
    )
    type = serializers.PrimaryKeyRelatedField(
        queryset=Type.objects.all(),
        required=True # Producto debe tener tipo
    )

    # Relación con subproductos (solo lectura en este serializer)
    subproducts = SubProductSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        # Listamos campos del modelo Y campos de representación de auditoría de BaseSerializer
        fields = [
            'id', 'name', 'code', 'description', 'brand', 'image', 'quantity', # Campos del modelo
            'category', 'type', # FKs (se mostrarán como IDs por defecto)
            'status', # Heredado de BaseModel
            'subproducts', # Campo related read_only
            'created_at', 'modified_at', 'deleted_at', # Campos de auditoría (BaseModel)
            # Campos de representación de usuarios (definidos en BaseSerializer)
            'created_by_username',
            'modified_by_username',
            'deleted_by_username'
        ]
        # Definimos campos de solo lectura explícitamente
        read_only_fields = [
            'created_at', 'modified_at', 'deleted_at',
            'created_by_username', 'modified_by_username', 'deleted_by_username',
            'subproducts' # Confirmamos que subproducts es solo lectura aquí
        ]

    # --- Validaciones Específicas (usando helpers de BaseSerializer) ---
    def validate_name(self, value):
        """Aplica la validación de nombre único normalizado heredada."""
        # Asegura que haya un valor antes de validar si el campo no es obligatorio
        if value:
             return self._get_normalized_name(value)
        return value # Permite blank/null si el modelo lo hace

    def validate_code(self, value):
        """Aplica la validación de código único heredada."""
        # Asegura que haya un valor antes de validar si el campo no es obligatorio
        if value is not None: # Código es IntegerField
             self._validate_unique_code(value) # Llama al helper, no devuelve nada
        return value # Permite null si el modelo lo hace
