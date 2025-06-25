import logging
from django.db import IntegrityError
from rest_framework import serializers

from apps.users.models.user_model import User
from apps.storages_client.services.profile_image import (
    upload_profile_image, delete_profile_image
)
from .user_base_serializers import UserSerializer

logger = logging.getLogger(__name__)


class UserUpdateSerializer(UserSerializer):
    image = serializers.ImageField(required=False, allow_null=True, write_only=True)
    password = serializers.CharField(write_only=True, required=False, min_length=4)

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ['image', 'password']

    def update(self, instance, validated_data):
        image_file = validated_data.pop('image', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        try:
            instance.save()
        except IntegrityError as e:
            if 'users_user.dni' in str(e):
                raise serializers.ValidationError({"dni": "Este DNI ya está en uso."})
            raise

        # Lógica para manejo de imagen
        try:
            eliminar_imagen = 'image' in self.initial_data and self.initial_data['image'] in [None, '', 'null']
            
            if eliminar_imagen and instance.image:
                delete_profile_image(instance.image, instance.id)
                instance.image = None
                instance.save(update_fields=["image"])
            
            elif image_file:
                if instance.image:
                    delete_profile_image(instance.image, instance.id)
                result = upload_profile_image(image_file, instance.id)
                instance.image = result.get('key')
                instance.save(update_fields=["image"])
        except Exception as e:
            logger.warning(f"No se pudo manejar la imagen de perfil: {e}")

        return instance
