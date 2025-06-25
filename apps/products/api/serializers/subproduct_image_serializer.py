from rest_framework import serializers
from apps.products.models.subproduct_image_model import SubproductImage

class SubproductImageSerializer(serializers.ModelSerializer):
    filename = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = SubproductImage
        fields = [
            'id', 'key', 'url', 'name', 'mime_type', 'created_at',
            'filename', 'content_type'
        ]
        read_only_fields = fields

    def get_filename(self, obj):
        return obj.name or obj.key

    def get_content_type(self, obj):
        return obj.mime_type or 'application/octet-stream'
