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
        Return a fully-qualified public URL for the profile image.
        If the storage backend returns a relative path, we prepend the
        current request’s host so browsers can fetch it correctly.
        """
        if not obj.image:
            return None

        url = default_storage.url(obj.image)
        request = self.context.get('request')
        if request and url.startswith('/'):
            return request.build_absolute_uri(url)
        return url