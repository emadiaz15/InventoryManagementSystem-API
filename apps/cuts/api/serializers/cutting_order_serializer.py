# apps/cuts/api/serializers/cutting_order_serializer.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.stocks.models import SubproductStock
from apps.products.models.subproduct_model import Subproduct
from apps.cuts.models.cutting_order_model import CuttingOrder, CuttingOrderItem
from apps.products.api.serializers.base_serializer import BaseSerializer

User = get_user_model()

class CuttingOrderItemSerializer(serializers.ModelSerializer):
    subproduct = serializers.PrimaryKeyRelatedField(
        queryset=Subproduct.objects.filter(status=True)
    )

    class Meta:
        model = CuttingOrderItem
        fields = ['id', 'subproduct', 'cutting_quantity']
        read_only_fields = ['id']

    def validate_cutting_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad de corte debe ser mayor a cero.")
        return value


class CuttingOrderSerializer(BaseSerializer):
    """
    Serializer para CuttingOrder con manejo de varios items.
    Usa BaseSerializer para auditoría automática (created_by, modified_by).
    """
    items = CuttingOrderItemSerializer(many=True)
    customer = serializers.CharField()
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        required=False, allow_null=True
    )
    workflow_status = serializers.ChoiceField(
        choices=CuttingOrder.WORKFLOW_STATUS_CHOICES,
        required=False
    )
    order_number = serializers.IntegerField()
    workflow_status_display = serializers.CharField(
        source='get_workflow_status_display', read_only=True
    )

    class Meta:
        model = CuttingOrder
        fields = [
            'id', 'customer', 'workflow_status', 'workflow_status_display',
            'assigned_to', 'completed_at',
            'items',
            'status', 'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by','order_number'
        ]
        read_only_fields = [
            'id', 'status', 'completed_at',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by',
            'workflow_status_display',
        ]

    def validate(self, data):
        items = data.get('items', [])
        if not items:
            raise serializers.ValidationError("Debe incluir al menos un item de corte.")

        # Validar stock para cada item
        for item in items:
            sp = item['subproduct']
            qty = item['cutting_quantity']
            try:
                stock = SubproductStock.objects.filter(
                    subproduct=sp, status=True
                ).latest('created_at')
                available = stock.quantity
            except SubproductStock.DoesNotExist:
                available = 0

            if qty > available:
                raise serializers.ValidationError({
                    'items': f"Stock insuficiente para '{sp}'. Disponible: {available}, Requerido: {qty}"
                })
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context.get('user')
        # BaseSerializer.create() asignará created_by=user automáticamente
        order = super().create(validated_data)

        # Crear cada item
        for item in items_data:
            CuttingOrderItem.objects.create(
                order=order,
                subproduct=item['subproduct'],
                cutting_quantity=item['cutting_quantity']
            )
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        # Actualizar campos básicos de la orden
        order = super().update(instance, validated_data)

        if items_data is not None:
            # Reemplazar items existentes
            order.items.all().delete()
            for item in items_data:
                CuttingOrderItem.objects.create(
                    order=order,
                    subproduct=item['subproduct'],
                    cutting_quantity=item['cutting_quantity']
                )
        return order
