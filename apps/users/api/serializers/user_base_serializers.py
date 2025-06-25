from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
import re

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Este nombre de usuario ya está en uso.")],
        error_messages={
            "required": "El nombre de usuario es obligatorio.",
            "blank": "El nombre de usuario no puede estar vacío."
        }
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Este correo electrónico ya está en uso.")],
        error_messages={
            "required": "El correo electrónico es obligatorio.",
            "blank": "El correo electrónico no puede estar vacío.",
            "invalid": "Ingrese un correo electrónico válido."
        }
    )
    dni = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Este DNI ya está en uso.")],
        required=False,
        allow_blank=True,
    )
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'last_name', 'dni', 'is_staff', 'is_active', 'image_url']
        read_only_fields = ['id', 'image_url']

    def get_image_url(self, obj):
        if not obj.image or not isinstance(obj.image, str):
            return None
        return obj.image  # Ya es una URL pública generada desde MinIO
       
    def validate_dni(self, value):
        if value and not re.match(r"^\d{7,10}$", value):
            raise serializers.ValidationError("El DNI debe contener entre 7 y 10 dígitos.")
        return value
