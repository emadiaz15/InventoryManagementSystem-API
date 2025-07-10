from rest_framework import serializers

class UserProfileImageSerializer(serializers.Serializer):
    file = serializers.ImageField(required=True, allow_empty_file=False)