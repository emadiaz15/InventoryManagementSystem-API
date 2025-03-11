from rest_framework import serializers
from apps.products.models.subproduct_model import Subproduct
from apps.products.api.serializers.base_serializer import BaseSerializer

class SubProductSerializer(BaseSerializer):
    """Serializer para subproductos con atributos de cable."""

    class Meta:
        model = Subproduct
        fields = [
            'id', 'name', 'description', 'status', 'brand', 'number_coil', 'initial_length', 'final_length', 'total_weight', 'coil_weight',
            'technical_sheet_photo', 'quantity', 'created_at', 'modified_at', 'deleted_at', 'created_by', 'modified_by', 'deleted_by',
        ]
