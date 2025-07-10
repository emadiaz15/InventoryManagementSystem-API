from rest_framework import serializers
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model

User = get_user_model()

class UserDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'name', 'last_name',
            'dni', 'image', 'image_url', 'is_staff', 'is_active'
        ]
        read_only_fields = fields

    def get_image_url(self, obj):
        """
        Retorna la URL pública y estable de la imagen de perfil.
        Por defecto, Django storage hará uso de AWS_S3_CUSTOM_DOMAIN y AWS_QUERYSTRING_AUTH=False,
        devolviendo algo como:
          https://bucket-production-c0e7.up.railway.app/img-profiles/profile-images/1_abc123.png
        """
        if not obj.image:
            return None
        return default_storage.url(obj.image)
