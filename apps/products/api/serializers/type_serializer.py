from rest_framework import serializers
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type
from .base_serializer import BaseSerializer

class TypeSerializer(BaseSerializer): # Hereda create, update y to_representation corregidos
    # El campo category se maneja correctamente por DRF y nuestro BaseSerializer
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)

    # La representación de estos campos la maneja BaseSerializer.to_representation
    # usando los campos *_username definidos allí.

    class Meta:
        model = Type
        # Listamos los campos del modelo Y los campos de REPRESENTACIÓN de auditoría
        # definidos en BaseSerializer (created_by_username, etc.)
        # BaseSerializer.to_representation luego los renombrará a created_by, etc. en el JSON final.
        fields = [
            'id', 'name', 'description', 'category', 'status',
            'created_at', 'modified_at', 'deleted_at',
            # Incluimos los campos de representación de BaseSerializer
            'created_by_username',
            'modified_by_username',
            'deleted_by_username'
        ]
        # Opcional: definir explícitamente read_only_fields para claridad
        read_only_fields = [
            'created_at', 'modified_at', 'deleted_at',
            'created_by_username', 'modified_by_username', 'deleted_by_username'
            ]
