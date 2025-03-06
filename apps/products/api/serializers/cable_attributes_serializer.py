from rest_framework import serializers
from apps.products.models import  CableAttributes
from .base_serializer import BaseSerializer  # 🚀 Importamos la clase base

class CableAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CableAttributes
        fields = '__all__'
        extra_kwargs = {'status': {'required': False}}
