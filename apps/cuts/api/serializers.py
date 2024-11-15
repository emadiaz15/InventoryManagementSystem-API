from rest_framework import serializers
from apps.cuts.models import CuttingOrder, Item
from apps.products.models import SubProduct
from django.utils.timezone import now

class CuttingOrderSerializer(serializers.ModelSerializer):
    """
    Serializador para manejar la conversión de CuttingOrder a JSON y viceversa,
    incluye validaciones y campos de solo lectura.
    """

    # Campos de solo lectura
    assigned_by = serializers.StringRelatedField(read_only=True)
    operator = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)

    # Campo para seleccionar subproducto (opcional)
    subproduct = serializers.PrimaryKeyRelatedField(queryset=SubProduct.objects.all(), required=False)

    # Incluir el campo items como una lista de identificadores de Item
    items = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all(), many=True)

    class Meta:
        model = CuttingOrder
        fields = '__all__'
        read_only_fields = ['status', 'completed_at', 'created_at', 'updated_at', 'assigned_by', 'operator']

    def validate_cutting_quantity(self, value):
        """
        Valida que la cantidad a cortar sea positiva.
        """
        if value <= 0:
            raise serializers.ValidationError("La cantidad de corte debe ser mayor que cero.")
        return value

    def create(self, validated_data):
        """
        Crea una nueva orden de corte asignando el usuario que realiza la creación.
        """
        # Obtener los items de la orden desde validated_data
        items_data = validated_data.pop('items', [])
        
        # Asignar el usuario que crea la orden
        user = self.context['request'].user  # Usuario autenticado en el contexto
        validated_data['assigned_by'] = user
        
        # Crear la orden de corte
        cutting_order = super().create(validated_data)
        
        # Asignar los items a la nueva orden de corte
        cutting_order.items.set(items_data)
        
        return cutting_order

    def update(self, instance, validated_data):
        """
        Controla la actualización de una orden de corte. Si se completa, asigna la fecha.
        """
        # Obtener los items de la orden desde validated_data
        items_data = validated_data.pop('items', [])
        
        if validated_data.get('status') == 'completed' and instance.status != 'completed':
            instance.completed_at = now()  # Marca la fecha de finalización si se completa la orden
        
        # Actualizar la instancia de la orden de corte
        instance = super().update(instance, validated_data)
        
        # Asignar los nuevos items (si se actualizan)
        if items_data:
            instance.items.set(items_data)
        
        return instance
