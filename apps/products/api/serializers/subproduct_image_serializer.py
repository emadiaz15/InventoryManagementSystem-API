from rest_framework import serializers
from apps.products.models.subproduct_image_model import SubproductImage

class SubproductImageSerializer(serializers.ModelSerializer):
    """
    📸 Serializer para archivos multimedia de subproducto.
    Expone metadatos útiles para descarga y vista previa.
    """
    filename = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = SubproductImage
        fields = [
            'id',
            'drive_file_id',
            'url',
            'created_at',
            'filename',
            'content_type',
        ]
        read_only_fields = fields

    def get_filename(self, obj):
        return obj.name or obj.drive_file_id

    def get_content_type(self, obj):
        return obj.mimeType or 'application/octet-stream'
