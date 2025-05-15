from rest_framework import serializers
from apps.products.models.subproduct_image_model import SubproductImage


class SubproductImageSerializer(serializers.ModelSerializer):
    """
    Serializer para imágenes multimedia asociadas a un Subproducto.
    Campos:
    - id: identificador de la imagen.
    - drive_file_id: ID del archivo en Google Drive.
    - created_at: fecha de creación.
    """
    class Meta:
        model = SubproductImage
        fields = ['id', 'drive_file_id', 'created_at']
        read_only_fields = ['id', 'drive_file_id', 'created_at']
