from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.services.images_services import upload_profile_image
import re

User = get_user_model()

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
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Este nombre de usuario ya está en uso."
            )
        ],
        error_messages={
            "required": "El nombre de usuario es obligatorio.",
            "blank": "El nombre de usuario no puede estar vacío."
        }
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Este correo electrónico ya está en uso."
            )
        ],
        error_messages={
            "required": "El correo electrónico es obligatorio.",
            "blank": "El correo electrónico no puede estar vacío.",
            "invalid": "Ingrese un correo electrónico válido."
        }
    )
    dni = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            "required": "El DNI es obligatorio.",
            "blank": "El DNI no puede estar vacío."
        }
    )
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        write_only=True
    )
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'name', 'last_name',
            'dni', 'image', 'image_url', 'is_active', 'is_staff', 'password'
        ]

    def get_image_url(self, obj):
        # En FastAPI guardamos solo el file_id, aquí podrías construir la URL de descarga.
        return obj.image if obj.image else None

    def validate_dni(self, value):
        if not re.match(r"^\d{7,10}$", value):
            raise serializers.ValidationError("El DNI debe contener entre 7 y 10 dígitos.")
        return value

    def create(self, validated_data):
        image_file = validated_data.pop('image', None)
        password   = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if image_file:
            result = upload_profile_image(image_file, user.id)
            user.image = result.get('file_id')
            user.save()

        return user

    def update(self, instance, validated_data):
        image_file = validated_data.pop('image', None)
        password   = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if image_file:
            result = upload_profile_image(image_file, instance.id)
            instance.image = result.get('file_id')
            instance.save()

        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializador personalizado para JWT con mensajes de error en español
    cuando el usuario no existe o la contraseña es incorrecta.
    """
    def validate(self, attrs):
        username_or_email = attrs.get(self.username_field)
        password = attrs.get("password")

        # 1) Intentar localizar al usuario por username o email
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

        # 2) Verificar contraseña
        if not user.check_password(password):
            raise serializers.ValidationError(
                {"detail": "Contraseña incorrecta."},
                code="incorrect_password"
            )

        # 3) Credenciales válidas: generar tokens
        #    Asegurarnos de usar el username real
        attrs[self.username_field] = user.username
        data = super().validate(attrs)

        return {
            "refresh_token": data.get("refresh"),
            "access_token":  data.get("access"),
        }
