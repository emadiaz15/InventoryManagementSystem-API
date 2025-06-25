from rest_framework import serializers
from apps.products.models.category_model import Category

from .base_serializer import BaseSerializer 

class CategorySerializer(BaseSerializer):

    # Los campos 'name', 'description' se heredan implícitamente de ModelSerializer
    # La representación y manejo de auditoría los hace BaseSerializer.

    class Meta:
        model = Category
        # Listamos los campos del modelo que queremos exponer
        # Y los campos de REPRESENTACIÓN de auditoría definidos en BaseSerializer
        fields = [
            'id', 'name', 'description', 'status', # Campos propios del modelo Category
            'created_at', 'modified_at', 'deleted_at', # Campos de auditoría (BaseModel)
            # Campos de representación de usuarios (definidos en BaseSerializer)
            'created_by_username',
            'modified_by_username',
            'deleted_by_username'
        ]
        # Definimos explícitamente campos de solo lectura para claridad
        # (Aunque BaseSerializer ya define los *_username como read_only
        # y los de fecha/hora no deberían ser editables directamente)
        read_only_fields = [
            'created_at', 'modified_at', 'deleted_at',
            'created_by_username', 'modified_by_username', 'deleted_by_username'
            ]

    # --- Validación Específica para 'name' ---
    def validate_name(self, value):
        """
        Aplica la validación de nombre único normalizado heredada.
        """
        # Llama al helper heredado de BaseSerializer
        # Asume que _get_normalized_name está en BaseSerializer
        return self._get_normalized_name(value)
