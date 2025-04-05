from rest_framework import serializers
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseSerializer(serializers.ModelSerializer):
    """Clase base para serializers con métodos reutilizables."""

    # Métodos _normalize_field, _get_normalized_name, _validate_unique_code (sin cambios)
    def _normalize_field(self, value):
        return value.strip().lower().replace(" ", "")

    def _get_normalized_name(self, name):
        # Esta validación puede necesitar ajustes si se usa fuera de modelos con 'name'
        # O podría moverse a serializers específicos
        if not hasattr(self.Meta, 'model') or not hasattr(self.Meta.model, 'name'):
             return name # O lanzar error si se espera un modelo con nombre

        normalized_name = self._normalize_field(name)
        ModelClass = self.Meta.model
        query = Q(name__iexact=normalized_name)
        if self.instance:
            query &= ~Q(id=self.instance.id)

        if ModelClass.objects.filter(query).exists():
            raise serializers.ValidationError(f"El nombre '{name}' ya existe. Debe ser único.")
        return name # Devuelve el nombre original después de validar unicidad normalizada

    def _validate_unique_code(self, code):
         if not hasattr(self.Meta, 'model') or not hasattr(self.Meta.model, 'code'):
             return # No hacer nada si el modelo no tiene 'code'
         ModelClass = self.Meta.model
         query = Q(code=code)
         if self.instance:
            query &= ~Q(id=self.instance.id)

         if ModelClass.objects.filter(query).exists():
            raise serializers.ValidationError(f"El código '{code}' ya existe. Debe ser único.")


    # --- Método update REFINADO ---
    def update(self, instance, validated_data):
        """
        Sobrescribe el método update para manejar campos de auditoría y soft delete.
        Utiliza super().update() para la asignación de campos normales.
        """
        # Obtenemos el usuario desde el contexto (pasado desde serializer.save(user=...))
        # O desde el request si está en el contexto
        user = validated_data.pop('user', self.context.get('request').user if self.context.get('request') else None)

        # Variable para rastrear si hubo cambios modificables por el usuario
        made_modification = False

        # Comprueba si 'status' está en los datos validados y es False (Soft Delete)
        if validated_data.get('status') is False:
            instance.status = False # Asegura que el estado se actualice
            instance.deleted_at = timezone.now()
            if user and isinstance(user, User): # Verifica que user sea una instancia válida
                instance.deleted_by = user
            made_modification = True # El cambio de estado cuenta como modificación auditable
            print(f"Soft deleting instance {instance.pk} by user {user.pk if user else 'None'}") # Log
        elif 'status' in validated_data and validated_data.get('status') is True:
             # Si se está reactivando (status=True)
             instance.status = True
             instance.deleted_at = None # Limpia fecha de eliminación
             instance.deleted_by = None # Limpia usuario de eliminación
             made_modification = True


        # Comprueba si otros campos (además de status y campos de auditoría) han cambiado
        audit_fields_to_ignore = {'status', 'modified_at', 'modified_by', 'deleted_at', 'deleted_by'}
        for field_name in validated_data:
            if field_name not in audit_fields_to_ignore:
                 # Compara el valor validado con el valor actual en la instancia
                 if getattr(instance, field_name) != validated_data[field_name]:
                     made_modification = True
                     break # Basta con que un campo haya cambiado

        # Si hubo una modificación relevante, actualiza modified_by y modified_at
        if made_modification:
            if user and isinstance(user, User): # Verifica que user sea instancia válida
                instance.modified_by = user
            instance.modified_at = timezone.now()
            print(f"Updating instance {instance.pk} modified by user {user.pk if user else 'None'}") # Log

        # Deja que el método update de DRF maneje la asignación de los campos validados
        # Esto incluye la asignación correcta de PrimaryKeyRelatedField (como 'category')
        # Quitamos explícitamente los campos de auditoría de validated_data antes de llamar a super,
        # ya que los estamos manejando manualmente en la instancia.
        validated_data.pop('modified_by', None)
        validated_data.pop('modified_at', None)
        validated_data.pop('deleted_by', None)
        validated_data.pop('deleted_at', None)
        # El status ya se asignó a la instancia si venía en validated_data

        # Llamamos a super().update() SOLO con los campos que realmente pertenecen al modelo
        # y que no son de auditoría manejados manualmente.
        # DRF se encargará de asignar 'name', 'description', 'category' (como ID), etc.
        instance = super().update(instance, validated_data)

        # No necesitamos instance.save() aquí, super().update() ya lo hace internamente.

        return instance

    # to_representation (sin cambios)
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_by'] = instance.created_by.username if instance.created_by else None
        data['modified_by'] = instance.modified_by.username if instance.modified_by else None
        data['deleted_by'] = instance.deleted_by.username if instance.deleted_by else None
        return data