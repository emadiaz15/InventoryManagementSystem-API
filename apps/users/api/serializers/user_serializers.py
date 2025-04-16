from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from apps.users.models.user_model import User
from apps.users.services.image_uploader import upload_profile_image
import re


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=4)
    image = serializers.ImageField(required=False, allow_null=True, write_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'name', 'last_name',
            'dni', 'image', 'image_url', 'is_active', 'is_staff', 'password'
        ]
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'username': {'required': True, 'allow_blank': False},
            'dni': {'required': True, 'allow_blank': False},
        }

    def get_image_url(self, obj):
        return obj.image if obj.image else None

    def validate_password(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Password must be at least 4 characters long.")
        return value

    def validate_unique_field(self, field_name, value):
        if User.objects.filter(**{field_name: value}).exclude(id=getattr(self.instance, 'id', None)).exists():
            raise serializers.ValidationError(f"This {field_name} is already in use.")
        return value

    def validate_email(self, value):
        return self.validate_unique_field('email', value)

    def validate_username(self, value):
        return self.validate_unique_field('username', value)

    def validate_dni(self, value):
        if not re.match(r"^\d{7,10}$", value):
            raise serializers.ValidationError("DNI must be between 7 and 10 digits.")
        return value

    def create(self, validated_data):
        image_file = validated_data.pop('image', None)
        password = validated_data.pop('password', None)

        user = User(**validated_data)

        if password:
            user.set_password(password)

        if image_file:
            result = upload_profile_image(image_file)
            user.image = result.get('file_id')  # Se asume que retorna la URL de la imagen

        user.save()
        return user

    def update(self, instance, validated_data):
        image_file = validated_data.pop('image', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        if image_file:
            result = upload_profile_image(image_file)
            instance.image = result.get('file_id')

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
        data = super().validate(attrs)
        return {
            "refresh_token": data.pop("refresh"),
            "access_token": data.pop("access"),
        }
