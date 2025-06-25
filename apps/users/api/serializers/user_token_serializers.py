from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.storages_client.services.profile_image import get_profile_image_url

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        token['email'] = user.email
        return token

    def validate(self, attrs):
        username_or_email = attrs.get(self.username_field)
        password = attrs.get("password")

        try:
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"detail": "El usuario no existe."},
                    code="user_not_found"
                )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"detail": "Contraseña incorrecta."},
                code="incorrect_password"
            )

        attrs[self.username_field] = user.username
        data = super().validate(attrs)

        return {
            "refresh_token": data.get("refresh"),
            "access_token": data.get("access"),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
                "image": user.image,
                "image_url": get_profile_image_url(user.image) if user.image else None
            }
        }
