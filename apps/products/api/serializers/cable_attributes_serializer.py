from rest_framework import serializers
from apps.products.models import CableAttributes
from .base_serializer import BaseSerializer
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
import base64

class CableAttributesSerializer(BaseSerializer):
    # Agregar campo de imagen base64 para convertirla antes de guardarla
    technical_sheet_photo_base64 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CableAttributes
        fields = '__all__'
        extra_kwargs = {'status': {'required': False}}

    def validate_technical_sheet_photo_base64(self, value):
        """Validación de la imagen base64 antes de ser guardada"""
        if value:
            try:
                # Asegúrate de que la imagen base64 sea válida y decodificable
                format, imgstr = value.split(';base64,')
                ext = format.split('/')[-1]
                if ext not in ['jpeg', 'png', 'jpg']:
                    raise ValidationError("La imagen debe ser en formato JPEG o PNG.")
                return value
            except Exception as e:
                raise ValidationError("Formato base64 de la imagen no válido.")
        return value

    def create(self, validated_data):
        """Sobrescribimos el método create para manejar la imagen base64"""
        technical_sheet_photo_base64 = validated_data.pop('technical_sheet_photo_base64', None)

        # Creamos el subproducto CableAttributes
        cable_attributes = super().create(validated_data)

        # Si tenemos la imagen base64, la decodificamos y asignamos
        if technical_sheet_photo_base64:
            format, imgstr = technical_sheet_photo_base64.split(';base64,')
            ext = format.split('/')[-1]
            cable_attributes.technical_sheet_photo = ContentFile(base64.b64decode(imgstr), name=f"{cable_attributes.parent.name}_tech_sheet.{ext}")
            cable_attributes.save()

        return cable_attributes

    def update(self, instance, validated_data):
        """Sobrescribimos el método update para manejar la imagen base64"""
        technical_sheet_photo_base64 = validated_data.pop('technical_sheet_photo_base64', None)

        # Actualizamos el CableAttributes
        instance = super().update(instance, validated_data)

        # Si tenemos una nueva imagen base64, la decodificamos y asignamos
        if technical_sheet_photo_base64:
            format, imgstr = technical_sheet_photo_base64.split(';base64,')
            ext = format.split('/')[-1]
            instance.technical_sheet_photo = ContentFile(base64.b64decode(imgstr), name=f"{instance.parent.name}_tech_sheet.{ext}")
            instance.save()

        return instance

    def to_representation(self, instance):
        """Ajusta la representación del objeto para asegurar valores correctos."""
        data = super().to_representation(instance)

        # Ajustamos el campo 'modified_by' y 'deleted_by' para evitar valores nulos innecesarios
        if instance.modified_by is None:
            data['modified_by'] = None

        if not instance.deleted_by and instance.status != False:
            data['deleted_by'] = None

        return data
