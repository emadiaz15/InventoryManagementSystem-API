from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    # Mantiene el UserSerializer sin cambios
    password = serializers.CharField(write_only=True, required=False, min_length=4)
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

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def validate_password(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Password must be at least 4 characters.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(id=getattr(self.instance, 'id', None)).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exclude(id=getattr(self.instance, 'id', None)).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value

    def validate_dni(self, value):
        if not value.isdigit() or len(value) < 7 or len(value) > 10:
            raise serializers.ValidationError("DNI must be 7 to 10 digits.")
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to obtain JWT token pairs with renamed fields for tokens.
    Adds custom claims to the token.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Rename the token keys
        data = {
            "refresh_token": data.pop("refresh"),
            "access_token": data.pop("access"),
        }
        
        return data
