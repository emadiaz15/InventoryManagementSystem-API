from rest_framework import serializers
from apps.products.models.product_image_model import ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'key', 'url', 'name', 'mime_type', 'created_at']
        read_only_fields = fields
