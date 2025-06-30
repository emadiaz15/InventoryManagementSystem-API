from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal, InvalidOperation
from collections import defaultdict

from apps.stocks.models import SubproductStock
from apps.products.models.subproduct_model import Subproduct
from apps.products.models.product_model import Product
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
    items = CuttingOrderItemSerializer(many=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(status=True))
    operator_can_edit_items = serializers.BooleanField(required=False)
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
            'id', 'product', 'operator_can_edit_items',
            'customer', 'workflow_status', 'workflow_status_display',
            'assigned_to', 'completed_at',
            'items',
            'status', 'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by', 'order_number'
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

        product = data.get('product') or getattr(self.instance, 'product', None)

        qty_per_subproduct = defaultdict(Decimal)

        for item in items:
            try:
                qty = Decimal(str(item['cutting_quantity']))
                if qty <= 0:
                    raise ValueError
            except (InvalidOperation, ValueError):
                raise serializers.ValidationError("Cantidad inválida en uno de los items.")

            subproduct = item['subproduct']
            if product and subproduct.parent_id != product.id:
                raise serializers.ValidationError({
                    'items': f"El subproducto {subproduct.id} no pertenece al producto indicado."
                })
            qty_per_subproduct[subproduct.id] += qty

        for subproduct_id, total_needed in qty_per_subproduct.items():
            stocks = SubproductStock.objects.filter(subproduct_id=subproduct_id, status=True)
            total_available = sum(s.quantity for s in stocks)

            if total_needed > total_available:
                raise serializers.ValidationError({
                    'items': f"Stock insuficiente para el subproducto ID {subproduct_id}. "
                             f"Necesita {total_needed}, disponible {total_available}."
                })

        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = super().create(validated_data)
        CuttingOrderItem.objects.bulk_create([
            CuttingOrderItem(
                order=order,
                subproduct=item['subproduct'],
                cutting_quantity=item['cutting_quantity']
            ) for item in items_data
        ])
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        order = super().update(instance, validated_data)

        if items_data is not None:
            # Reemplazar todos los items
            order.items.all().delete()
            CuttingOrderItem.objects.bulk_create([
                CuttingOrderItem(
                    order=order,
                    subproduct=item['subproduct'],
                    cutting_quantity=item['cutting_quantity']
                ) for item in items_data
            ])

        return order
