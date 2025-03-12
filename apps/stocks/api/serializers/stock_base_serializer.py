from rest_framework import serializers

class BaseSerializer(serializers.ModelSerializer):
    """Un serializer base para funcionalidades comunes entre modelos"""
    created_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    modified_at = serializers.DateTimeField(read_only=True)
    modified_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        abstract = True
