import logging
from django.db import IntegrityError, transaction
from rest_framework import serializers

from apps.users.models.user_model import User
from .user_base_serializers import UserSerializer
from apps.storages_client.services.profile_image import upload_profile_image

logger = logging.getLogger(__name__)

class UserCreateSerializer(UserSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=4,
        error_messages={
            "required": "La contraseña es obligatoria.",
            "min_length": "La contraseña debe tener al menos 4 caracteres."
        }
    )
    image = serializers.ImageField(required=False, allow_null=True, write_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ['password', 'image']

    def create(self, validated_data):
        image_file = validated_data.pop('image', None)
        password = validated_data.pop('password')
        validated_data['is_active'] = True

        with transaction.atomic():
            user = User(**validated_data)
            user.set_password(password)
            try:
                user.save()
            except IntegrityError as e:
                if 'users_user.dni' in str(e):
                    raise serializers.ValidationError({"dni": "Este DNI ya está en uso."})
                raise

        if image_file:
            try:
                result = upload_profile_image(image_file, user.id)
                user.image = result.get('key')  # Guardamos el 'key' que representa el path en MinIO
                user.save(update_fields=['image'])
            except Exception as e:
                logger.warning(f"No se pudo subir la imagen de perfil: {e}")

        return user
