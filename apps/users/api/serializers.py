from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo User.
    Maneja la conversión de los datos del modelo User a formato JSON y viceversa.
    """
    password = serializers.CharField(write_only=True, required=False, min_length=4)  # Cambiado a opcional para actualizar
    image = serializers.ImageField(required=False, allow_null=True)  # Hacer opcional el campo de imagen

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'last_name', 'dni', 'image', 'is_active', 'is_staff', 'password']
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'username': {'required': True, 'allow_blank': False},
            'dni': {'required': True, 'allow_blank': False},
            'image': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        """
        Crea un nuevo usuario encriptando la contraseña antes de guardarlo.
        """
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)  # Encriptar la contraseña solo si es proporcionada
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Actualiza un usuario. Encripta la contraseña si es proporcionada.
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # Solo actualiza la contraseña si se proporciona
        instance.save()
        return instance

    def validate_password(self, value):
        """
        Validación adicional para la contraseña.
        """
        if len(value) < 4:
            raise serializers.ValidationError("La contraseña debe tener al menos 4 caracteres.")
        return value

    def validate_email(self, value):
        """
        Validación para asegurar que el email sea único.
        """
        # Comprobar si el email ya existe en otro usuario
        if User.objects.filter(email=value).exclude(id=getattr(self.instance, 'id', None)).exists():
            raise serializers.ValidationError("Este correo electrónico ya está en uso.")
        return value

    def validate_username(self, value):
        """
        Validación para asegurar que el username sea único.
        """
        # Comprobar si el username ya existe en otro usuario
        if User.objects.filter(username=value).exclude(id=getattr(self.instance, 'id', None)).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value

    def validate_dni(self, value):
        """
        Validación personalizada para el DNI (opcional).
        """
        if not value.isdigit():
            raise serializers.ValidationError("El DNI debe contener solo números.")
        if len(value) < 7 or len(value) > 10:
            raise serializers.ValidationError("El DNI debe tener entre 7 y 10 dígitos.")
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializador personalizado para obtener pares de tokens JWT.
    Añade claims personalizados al token.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Añadir claims personalizados al token
        token['name'] = user.name
        token['email'] = user.email

        return token
