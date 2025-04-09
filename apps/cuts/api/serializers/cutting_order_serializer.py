from rest_framework import serializers
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
 
from apps.cuts.models.cutting_order_model import CuttingOrder
from apps.products.models.subproduct_model import Subproduct

from apps.stocks.models import SubproductStock
from apps.products.api.serializers.base_serializer import BaseSerializer 

User = get_user_model()

class CuttingOrderSerializer(BaseSerializer):
    """
    Serializer para CuttingOrder, usando BaseSerializer para auditoría
    y manejando campos específicos como workflow_status y relaciones.
    """

    # --- Campos de Relaciones ---
    subproduct = serializers.PrimaryKeyRelatedField(
        queryset=Subproduct.objects.filter(status=True),
        required=True
    )
    assigned_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        required=False, allow_null=True
    )
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        required=False, allow_null=True
    )

    # --- Campos de Representación (Solo Lectura) ---
    subproduct_name = serializers.CharField(source='subproduct.name', read_only=True)
    # Usamos allow_null=True por si el usuario fue borrado (SET_NULL)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True, allow_null=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)

    # --- Campo de Flujo de Trabajo ---
    workflow_status = serializers.ChoiceField(
        choices=CuttingOrder.WORKFLOW_STATUS_CHOICES,
        required=False
    )
    workflow_status_display = serializers.CharField(source='get_workflow_status_display', read_only=True)


    class Meta:
        model = CuttingOrder
        fields = [
            'id',
            'customer', 'cutting_quantity', 'completed_at',
            'workflow_status', 'workflow_status_display',
            'subproduct', 'assigned_by', 'assigned_to',
            'subproduct_name', 'assigned_by_username', 'assigned_to_username',
            'status', # Booleano de BaseModel
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by', # Finales formateados
        ]
        read_only_fields = [
            'status', 'completed_at',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by', # Claves finales son read-only
            'subproduct_name', 'assigned_by_username', 'assigned_to_username',
            'workflow_status_display',
        ]

    # --- Validaciones ---
    def validate_cutting_quantity(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("La cantidad de corte debe ser mayor a cero.")
        return value

    def validate(self, data):
        """Validaciones a nivel de objeto (ej. stock disponible)."""
        instance = getattr(self, 'instance', None)
        # Determinar subproducto y cantidad (ya sea del input o de la instancia)
        subproduct = data.get('subproduct', getattr(instance, 'subproduct', None))
        cutting_quantity = data.get('cutting_quantity', getattr(instance, 'cutting_quantity', None))

        # Solo validar stock si tenemos ambos datos y la cantidad es positiva
        if subproduct and cutting_quantity is not None and cutting_quantity > 0:
            try:
                # Obtenemos el stock MÁS RECIENTE activo para ese subproducto
                # ¡Ojo! Asume un único registro de stock relevante por subproducto
                # o que el más reciente es el correcto. Puede necesitar ajuste.
                stock = SubproductStock.objects.filter(subproduct=subproduct, status=True).latest('created_at')
                available_quantity = stock.quantity
            except SubproductStock.DoesNotExist:
                available_quantity = 0

            # Validar stock suficiente al CREAR o si la cantidad AUMENTA al actualizar
            is_creating = instance is None
            current_quantity = getattr(instance, 'cutting_quantity', 0) if not is_creating else 0

            # Comprobación simplificada: ¿Hay suficiente stock para la cantidad total pedida?
            if cutting_quantity > available_quantity:
                 raise serializers.ValidationError({
                     # Asociamos el error al campo cantidad
                     'cutting_quantity': f"Stock insuficiente para '{subproduct}'. "
                                       f"Disponible: {available_quantity}, Requerido: {cutting_quantity}"
                 })

        return data


    # --- Método Create ---
    def create(self, validated_data):
        """Asigna created_by (via BaseSerializer) y assigned_by por defecto."""
        # user se obtiene del context['user'] dentro de super().create()
        user = self.context.get('user', None)
        if 'assigned_by' not in validated_data and user:
            validated_data['assigned_by'] = user
        return super().create(validated_data) # Llama a BaseSerializer.create
