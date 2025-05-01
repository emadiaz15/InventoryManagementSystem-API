import os
from rest_framework import serializers
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
        read_only_fields = fields  # Todos los campos son solo lectura

    def get_image_url(self, obj):
        """
        Retorna la URL pública de la imagen del usuario, si existe.
        Depende del context['include_image_url'] para habilitarla.
        """
        if not obj.image or not isinstance(obj.image, str):
            return None

        if self.context.get("include_image_url", False):
            public_url = os.environ.get("PUBLIC_DRIVE_URL", "http://localhost:8001").rstrip("/")
            return f"{public_url}/profile/download/{obj.image}"

        return None
