from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.storages_client.services.profile_image import get_profile_image_url

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
        Retorna una URL firmada (temporal) para acceder a la imagen de perfil
        solo si se pasó 'include_image_url=True' en el contexto.
        """
        if not obj.image or not isinstance(obj.image, str):
            return None

        if self.context.get("include_image_url", False):
            return get_profile_image_url(obj.image)

        return None
