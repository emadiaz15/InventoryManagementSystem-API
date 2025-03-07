from rest_framework import serializers
from apps.products.models.category_model import Category
from .base_serializer import BaseSerializer

class CategorySerializer(BaseSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    modified_by = serializers.CharField(source='modified_by.username', read_only=True)  # Este campo debe ser solo lectura
    deleted_by = serializers.CharField(source='deleted_by.username', read_only=True, required=False)
    modified_at = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'status',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by'
        ]
