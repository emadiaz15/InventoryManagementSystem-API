from rest_framework import serializers
from apps.products.models.subproduct_image_model import SubproductImage

class SubproductImageSerializer(serializers.ModelSerializer):
    """
    Serializer para imágenes multimedia asociadas a un Subproducto.
    Devuelve los metadatos necesarios para visualizar correctamente
    los archivos en el frontend.
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
        return getattr(obj, 'name', f"{obj.drive_file_id}")

    def get_content_type(self, obj):
        return getattr(obj, 'mimeType', 'application/octet-stream')
