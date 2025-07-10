from rest_framework import serializers
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model
from apps.storages_client.utils import generate_presigned_url

User = get_user_model()

class UserDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    image_signed_url = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'name', 'last_name',
            'dni', 'image', 'image_url', 'image_signed_url', 'is_staff', 'is_active'
        ]
        read_only_fields = fields

    def get_image_signed_url(self, obj):
        """Retorna una URL presignada para la imagen de perfil."""
        if not obj.image or not isinstance(obj.image, str):
            return None

        return generate_presigned_url(
            bucket=settings.AWS_PROFILE_BUCKET_NAME,
            object_name=obj.image
        )