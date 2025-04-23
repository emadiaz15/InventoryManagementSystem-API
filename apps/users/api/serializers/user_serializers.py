import logging
import re
import os
import base64
import requests
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.services.images_services import upload_profile_image, generate_jwt

User = get_user_model()
logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=4,
        error_messages={
            "required": "La contraseña es obligatoria.",
            "min_length": "La contraseña debe tener al menos 4 caracteres."
        }
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Este nombre de usuario ya está en uso.")],
        error_messages={"required": "El nombre de usuario es obligatorio.", "blank": "El nombre de usuario no puede estar vacío."}
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Este correo electrónico ya está en uso.")],
        error_messages={"required": "El correo electrónico es obligatorio.", "blank": "El correo electrónico no puede estar vacío.", "invalid": "Ingrese un correo electrónico válido."}
    )
    dni = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Este DNI ya está en uso.")],
        required=False,
        allow_blank=True,
    )
    image = serializers.ImageField(required=False, allow_null=True, write_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    image_data_base64 = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'name', 'last_name',
            'dni', 'image', 'image_url', 'image_data_base64', 'is_staff', 'password', 'is_active'
        ]
        read_only_fields = ['id', 'image_url', 'image_data_base64']

    def get_image_url(self, obj):
        request = self.context.get("request")
        if not obj.image or not request:
            return None

        # Si el serializer es usado en modo "detalle" explícito, se permite incluir la URL
        if self.context.get("include_image_url", False):
            return request.build_absolute_uri(f"/api/v1/users/image/{obj.image}/")

        return None

    def get_image_data_base64(self, obj):
        if not obj.image or not self.context.get("include_image_base64", False):
            return None

        try:
            token = generate_jwt(obj.id)
            drive_url = f"{os.environ.get('DRIVE_API_BASE_URL', '').rstrip('/')}/profile/download/{obj.image}"
            headers = {"x-api-key": f"Bearer {token}"}
            response = requests.get(drive_url, headers=headers)
            response.raise_for_status()
            return base64.b64encode(response.content).decode("utf-8")
        except Exception:
            return None

    def validate_dni(self, value):
        if value and not re.match(r"^\d{7,10}$", value):
            raise serializers.ValidationError("El DNI debe contener entre 7 y 10 dígitos.")
        return value

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
                user.image = result.get('file_id')
                user.save(update_fields=['image'])
            except Exception as e:
                logger.warning(f"No se pudo subir la imagen de perfil: {e}")

        return user

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

        if image_file:
            try:
                result = upload_profile_image(image_file, instance.id)
                instance.image = result.get('file_id')
                instance.save(update_fields=['image'])
            except Exception as e:
                logger.warning(f"No se pudo actualizar la imagen de perfil: {e}")

        return instance


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
            "fastapi_token": generate_jwt(user.id),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
                "image": user.image,
            }
        }


class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=4,
        write_only=True,
        required=True,
        error_messages={
            "required": "La contraseña es obligatoria.",
            "min_length": "La contraseña debe tener al menos 4 caracteres."
        }
    )
