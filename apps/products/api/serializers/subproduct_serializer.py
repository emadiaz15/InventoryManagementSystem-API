from rest_framework import serializers

from apps.products.models.subproduct_model import Subproduct
from .base_serializer import BaseSerializer 

class SubProductSerializer(BaseSerializer): 
    """
    Serializer para Subproducto, usando BaseSerializer para auditoría
    y manejando la asignación del 'parent'.
    """

    # El campo 'parent' no se envía en el JSON de creación/actualización,
    # se obtiene de la URL en la vista y se pasa via contexto/save().
    # Lo incluimos aquí como read_only para que aparezca en la respuesta GET.
    parent = serializers.PrimaryKeyRelatedField(read_only=True)

    # Los campos de auditoría para representación vienen de BaseSerializer

    class Meta:
        model = Subproduct
        # Listamos campos del modelo (excluyendo status redundante)
        # Y los campos de REPRESENTACIÓN de auditoría de BaseSerializer
        fields = [
            'id', 'name', 'description', 'brand', 'number_coil', # Campos específicos
            'initial_length', 'final_length', 'total_weight', 'coil_weight',
            'technical_sheet_photo', 'quantity',
            'parent', # FK (read_only en este serializer)
            'status', # Heredado de BaseModel
            'created_at', 'modified_at', 'deleted_at', # Campos de auditoría (BaseModel)
            # Campos de representación de usuarios (definidos en BaseSerializer)
            'created_by_username',
            'modified_by_username',
            'deleted_by_username'
        ]
        # Definimos campos de solo lectura explícitamente
        read_only_fields = [
            'parent', # El padre no se cambia via este serializer una vez creado
            'created_at', 'modified_at', 'deleted_at',
            'created_by_username', 'modified_by_username', 'deleted_by_username'
        ]

    # --- Validaciones Específicas ---
    def validate_name(self, value):
        if not value: raise serializers.ValidationError("El nombre es obligatorio.")
        # Considera añadir validación de unicidad normalizada DENTRO del padre si es necesario:
        # parent = self.context.get('parent_product', getattr(self.instance, 'parent', None))
        # if parent and Subproduct.objects.filter(parent=parent, name__iexact=self._normalize_field(value)).exists():
        #      raise serializers.ValidationError("Ya existe un subproducto con este nombre para el producto padre.")
        return value

    def validate_quantity(self, value):
        if value is None or value < 0: # Permitimos 0 si el stock se maneja aparte
             raise serializers.ValidationError("La cantidad no puede ser negativa.")
        return value

    # Puedes mantener las validaciones de peso/longitud si son relevantes
    def validate_total_weight(self, value):
        if value is not None and value <= 0: raise serializers.ValidationError("El peso total debe ser mayor que cero si se especifica.")
        return value
    # ... (otras validaciones similares para initial_length, final_length, coil_weight) ...
    def validate_initial_length(self, value):
        if value is not None and value < 0: raise serializers.ValidationError("Longitud inicial no puede ser negativa.")
        return value
    def validate_final_length(self, value):
        if value is not None and value < 0: raise serializers.ValidationError("Longitud final no puede ser negativa.")
        return value
    def validate_coil_weight(self, value):
        if value is not None and value < 0: raise serializers.ValidationError("Peso de bobina no puede ser negativo.")
        return value

    # --- Sobrescribir CREATE para asignar el PARENT ---
    def create(self, validated_data):
        """
        Asigna el 'parent' obtenido del contexto (añadido por la vista)
        antes de llamar al 'create' de BaseSerializer.
        """
        # Obtenemos el parent_product del contexto (la vista debe ponerlo ahí)
        parent_product = self.context.get('parent_product')
        if not parent_product:
            raise serializers.ValidationError("Contexto inválido: Falta 'parent_product'.")

        # Asignamos el parent a los datos validados ANTES de crear
        validated_data['parent'] = parent_product

        # Llamamos al 'create' de la clase padre (BaseSerializer)
        # Este se encargará de obtener el 'user' del contexto y llamar a instance.save(user=user)
        return super().create(validated_data)

