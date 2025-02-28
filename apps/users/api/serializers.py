from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from apps.users.models import User
import re


class UserSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de usuario con validaciones específicas.
    """
    password = serializers.CharField(write_only=True, required=True, min_length=4)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'last_name', 'dni', 'image', 'is_active', 'is_staff', 'password']
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'username': {'required': True, 'allow_blank': False},
            'dni': {'required': True, 'allow_blank': False},
            'image': {'required': False, 'allow_null': True},
        }

    def validate_password(self, value):
        """
        Valida que la contraseña tenga al menos 4 caracteres.
        """
        if len(value) < 4:
            raise serializers.ValidationError("Password must be at least 4 characters long.")
        return value

    def validate_unique_field(self, field_name, value):
        """
        Valida que un campo (email, username, etc.) sea único.
        """
        if User.objects.filter(**{field_name: value}).exclude(id=getattr(self.instance, 'id', None)).exists():
            raise serializers.ValidationError(f"This {field_name} is already in use.")
        return value

    def validate_email(self, value):
        """
        Valida que el email sea único.
        """
        return self.validate_unique_field('email', value)

    def validate_username(self, value):
        """
        Valida que el username sea único.
        """
        return self.validate_unique_field('username', value)

    def validate_dni(self, value):
        """
        Valida que el DNI sea un número de entre 7 y 10 dígitos.
        """
        if not re.match(r"^\d{7,10}$", value):
            raise serializers.ValidationError("DNI must be between 7 and 10 digits.")
        return value

    def create(self, validated_data):
        """
        Crea un nuevo usuario con una contraseña encriptada.
        """
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Actualiza un usuario existente y maneja la contraseña.
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializador personalizado para JWT.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        token['email'] = user.email
        return token

    def validate(self, attrs):
        """
        Renombra las claves de los tokens a 'refresh_token' y 'access_token'.
        """
        data = super().validate(attrs)
        return {
            "refresh_token": data.pop("refresh"),
            "access_token": data.pop("access"),
        }
