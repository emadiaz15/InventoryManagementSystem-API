from rest_framework import serializers
from decimal import Decimal
from django.core.exceptions import ValidationError as DjangoValidationError 

from apps.products.models.subproduct_model import Subproduct
from apps.products.models.product_model import Product

from .base_serializer import BaseSerializer

class SubProductSerializer(BaseSerializer):
    """
    Serializer final para Subproducto.
    - Usa BaseSerializer para auditoría.
    - Muestra stock actual calculado ('current_stock').
    - Acepta opcionalmente ajuste de stock en PUT ('quantity_change', 'reason').
    - Maneja la asignación del 'parent' durante la creación usando el contexto.
    """

    # --- Campos de Relación (Solo Lectura en la respuesta) ---
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    # --- Campo Calculado de Stock (Solo Lectura) ---
    current_stock = serializers.DecimalField(
        max_digits=15, decimal_places=2, # Ajusta según SubproductStock.quantity
        read_only=True,
        default=Decimal('0.00')
    )

    # --- CAMPOS SOLO PARA ENTRADA DE AJUSTE DE STOCK (en PUT) ---
    quantity_change = serializers.DecimalField(
        max_digits=15, decimal_places=2,
        write_only=True, # No se muestra en la respuesta JSON
        required=False, # Es opcional enviar estos campos en el PUT
        allow_null=True # Permite que no se envíe el campo
    )
    reason = serializers.CharField(
        max_length=255,
        write_only=True, # No se muestra en la respuesta JSON
        required=False, # Es opcional enviar estos campos en el PUT
        allow_null=True,
        allow_blank=True # Permite enviar una razón vacía si se desea (aunque validate lo requiere si hay quantity_change)
    )
    # ---------------------------------------------------------

    class Meta:
        model = Subproduct
        # Lista completa de campos para la API
        fields = [
            'id', 'name', 'description', 'brand', 'number_coil', # Campos específicos del modelo
            'initial_length', 'final_length', 'total_weight', 'coil_weight',
            'technical_sheet_photo',
            'parent', 'parent_name', # FK y su representación read-only
            'current_stock', # Stock actual read-only (calculado en vista GET)
            'status', # Booleano heredado (activo/inactivo)
            'created_at', 'modified_at', 'deleted_at', # Timestamps heredados
            'created_by', 'modified_by', 'deleted_by', # Auditoría (formateada por BaseSerializer)
            # Campos write_only (no aparecerán en respuesta GET, pero se aceptan en PUT)
            'quantity_change', 'reason',
        ]
        # Campos que son solo para mostrar o asignados automáticamente por el backend
        read_only_fields = [
            'parent', 'parent_name',
            'status', # El estado Activo/Inactivo se maneja via DELETE (soft delete)
            'current_stock',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by', # Las claves finales ya formateadas
        ]

    # --- Validaciones Específicas ---
    def validate_name(self, value):
        """Valida nombre obligatorio y unicidad dentro del padre."""
        if not value: raise serializers.ValidationError("El nombre es obligatorio.")
        # Validación de unicidad DENTRO del padre
        # Necesita 'parent_product' en el contexto si es creación, o usa self.instance.parent si es update
        parent = self.context.get('parent_product', getattr(self.instance, 'parent', None))
        # Usamos _get_normalized_name heredado de BaseSerializer
        normalized_value = self._normalize_field(value) if hasattr(self, '_normalize_field') else value
        if parent:
            queryset = Subproduct.objects.filter(parent=parent, name__iexact=normalized_value)
            if self.instance: # Excluirse a sí mismo en updates
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                 raise serializers.ValidationError(f"Ya existe un subproducto con este nombre para el producto padre '{parent}'.")
        return value

    # Validaciones de peso/longitud (mantenidas)
    def validate_total_weight(self, value):
        if value is not None and value < 0: raise serializers.ValidationError("El peso total no puede ser negativo.")
        return value
    def validate_initial_length(self, value):
        if value is not None and value < 0: raise serializers.ValidationError("Longitud inicial no puede ser negativa.")
        return value
    def validate_final_length(self, value):
        if value is not None and value < 0: raise serializers.ValidationError("Longitud final no puede ser negativa.")
        return value
    def validate_coil_weight(self, value):
        if value is not None and value < 0: raise serializers.ValidationError("Peso de bobina no puede ser negativo.")
        return value

    # Validación para quantity_change si se proporciona
    def validate_quantity_change(self, value):
        if value is not None and value == 0:
            raise serializers.ValidationError("La cantidad del ajuste no puede ser cero si se proporciona.")
        # La validación de stock negativo se hace en el servicio antes de guardar
        return value

    # Validación cruzada para quantity_change y reason
    def validate(self, data):
        """Valida que 'reason' exista si se provee 'quantity_change'."""
        quantity_change = data.get('quantity_change')
        reason = data.get('reason')

        # Si se intenta ajustar stock (quantity_change no es None y no es 0), se requiere razón
        if quantity_change is not None and quantity_change != 0 and not reason:
             # Usamos raise para detener la validación aquí
             raise serializers.ValidationError({"reason": ["Se requiere una razón para el ajuste de stock."]}) # DRF espera lista de errores

        # Opcional: requerir cantidad si se da una razón
        # if reason and quantity_change is None:
        #      raise serializers.ValidationError({"quantity_change": ["Se requiere una cantidad para el ajuste con esta razón."]})

        # Llamar a validaciones de modelo si es necesario (ej. clean())
        # super().validate(data) # ModelSerializer no llama a clean() por defecto

        return data


    # --- Sobrescribimos CREATE para asignar PARENT desde el contexto ---
    def create(self, validated_data):
        """
        Asigna el 'parent' obtenido del contexto (añadido por la vista)
        y luego llama al 'create' de BaseSerializer para manejar el 'user'.
        """
        parent_product = self.context.get('parent_product')
        if not parent_product:
            raise serializers.ValidationError("Error interno: Falta 'parent_product' en el contexto del serializador.")

        # Asignamos el parent ANTES de llamar al create padre
        validated_data['parent'] = parent_product

        # Llama a BaseSerializer.create, que obtiene 'user' del contexto y llama a instance.save(user=user)
        # No necesitamos pasar user aquí, BaseSerializer.create lo maneja.
        return super().create(validated_data)
