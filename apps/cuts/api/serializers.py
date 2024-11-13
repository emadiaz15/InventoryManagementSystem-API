from rest_framework import serializers
from apps.cuts.models import CuttingOrder

class CuttingOrderSerializer(serializers.ModelSerializer):
    """
    Serializador para manejar la conversión de CuttingOrder a JSON y viceversa.
    """
    class Meta:
        model = CuttingOrder
        fields = '__all__'
