from rest_framework import serializers
from apps.products.models.product_image_model import ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'drive_file_id', 'created_at']
