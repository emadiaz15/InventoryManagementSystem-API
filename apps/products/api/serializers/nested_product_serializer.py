from rest_framework import serializers

from apps.products.models import Product
from apps.products.api.serializers.category_serializer import CategorySerializer
from apps.products.api.serializers.type_serializer import TypeSerializer

class NestedProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    type = TypeSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'code', 'description', 'image', 'category', 'type', 'created_at', 'modified_at', 'deleted_at', 'status', 'user']

