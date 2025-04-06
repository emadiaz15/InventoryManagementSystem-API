from rest_framework import serializers
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()

class BaseSerializer(serializers.ModelSerializer):
    """
    Clase base para serializers v3.
    - create/update aceptan 'user' explícito.
    - save() extrae 'user' y lo pasa a create/update.
    - Delega a BaseModel.save() pasándole 'user'.
    - Maneja representación y validación.
    """
    # --- Representación de Campos de Auditoría ---
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    modified_by_username = serializers.CharField(source='modified_by.username', read_only=True)
    deleted_by_username = serializers.CharField(source='deleted_by.username', read_only=True)

    # --- Helpers de Validación ---
    def _normalize_field(self, value):
        if isinstance(value, str): return value.strip().lower().replace(" ", "")
        return value
    def _get_normalized_name(self, name):
        if not isinstance(name, str): raise serializers.ValidationError("El nombre debe ser texto.")
        if not hasattr(self.Meta, 'model') or not hasattr(self.Meta.model, 'name'): return name
        normalized_name = self._normalize_field(name)
        ModelClass = self.Meta.model
        query = Q(name__iexact=normalized_name)
        instance_pk = getattr(self.instance, 'pk', None)
        if instance_pk: query &= ~Q(pk=instance_pk)
        if ModelClass.objects.filter(query).exists(): raise serializers.ValidationError(f"El nombre '{name}' ya existe.")
        return name
    def _validate_unique_code(self, code):
         if not hasattr(self.Meta, 'model') or not hasattr(self.Meta.model, 'code'): return
         ModelClass = self.Meta.model
         query = Q(code=code)
         instance_pk = getattr(self.instance, 'pk', None)
         if instance_pk: query &= ~Q(pk=instance_pk)
         if ModelClass.objects.filter(query).exists(): raise serializers.ValidationError(f"El código '{code}' ya existe.")

    def save(self, **kwargs):
        """
        Extrae 'user' de kwargs y lo pasa explícitamente a create o update.
        """
        user = kwargs.pop('user', None) # Extrae user de save(user=...)
        # Aseguramos que 'user' no vaya en los kwargs restantes a super().save()
        # aunque DRF save() base no los usa directamente para create/update

        # Añadimos el user al contexto por si alguna validación lo necesita
        # (Aunque create/update ahora lo recibirán directamente)
        if user:
             self.context['user'] = user
        if 'request' not in self.context and user and hasattr(user, '_request'):
             self.context['request'] = getattr(user, '_request')


        # Llamamos al save original de DRF. Este validará y luego llamará
        # a nuestro self.create o self.update sobreescritos abajo.
        # PERO, necesitamos pasarle el 'user' a esos métodos.
        # Lo haremos modificando cómo se llaman create/update.

        # Validar datos primero (esto es parte de lo que hace super().save())
        assert hasattr(self, '_validated_data'), (
            'Cannot call `.save()` before `.is_valid()` has been called.'
        )
        validated_data = dict(self._validated_data) # Copiamos para no modificar el original

        try:
            if self.instance is not None:
                # Llamamos a NUESTRO update pasando el user
                self.instance = self.update(self.instance, validated_data, user=user)
                assert self.instance is not None, (
                    '`update()` did not return an object instance.'
                )
            else:
                # Llamamos a NUESTRO create pasando el user
                self.instance = self.create(validated_data, user=user)
                assert self.instance is not None, (
                    '`create()` did not return an object instance.'
                )
        except (TypeError, ValueError, DjangoValidationError) as exc:
             # Capturamos errores comunes y los relanzamos como ValidationError de DRF
             raise serializers.ValidationError(detail=serializers.as_serializer_error(exc))

        return self.instance


    # --- Método CREATE (Acepta 'user' explícito) ---
    def create(self, validated_data, user=None): # Acepta user aquí
        """
        Maneja la creación, usando el 'user' recibido explícitamente.
        """
        print(f"--- DEBUG SERIALIZER CREATE v3: Inicio ---")
        print(f"--- DEBUG SERIALIZER CREATE v3: user recibido explícitamente: {user} (ID: {getattr(user, 'pk', 'N/A')}) ---")
        # Ya no necesitamos obtenerlo del contexto ni popearlo de validated_data
        print(f"--- DEBUG SERIALIZER CREATE v3: validated_data para instanciar: {validated_data} ---")
        try:
            instance = self.Meta.model(**validated_data)
            print(f"--- DEBUG SERIALIZER CREATE v3: Instancia creada en memoria: {instance} ---")
            print(f"--- DEBUG SERIALIZER CREATE v3: Llamando a instance.save(user={user}) ---")
            # Llama al save() de BaseModel pasando el user recibido
            instance.save(user=user)
            print(f"--- DEBUG SERIALIZER CREATE v3: instance.save() completado. Instancia final: {instance} ---")
        except TypeError as e:
             print(f"--- ERROR SERIALIZER CREATE v3: TypeError: {e} ---")
             raise TypeError(f"Error al instanciar {self.Meta.model.__name__}: {e}")
        except DjangoValidationError as e:
             print(f"--- ERROR SERIALIZER CREATE v3: DjangoValidationError: {e} ---")
             raise serializers.ValidationError(e.detail)
        except Exception as e:
             print(f"--- ERROR SERIALIZER CREATE v3: Exception: {e} ---")
             raise serializers.ValidationError(f"Error inesperado al guardar: {e}")
        print("--- DEBUG SERIALIZER CREATE v3: Fin ---")
        return instance

    # --- Método UPDATE (Acepta 'user' explícito) ---
    def update(self, instance, validated_data, user=None): # Acepta user aquí
        """
        Maneja la actualización, usando el 'user' recibido explícitamente.
        """
        print(f"--- DEBUG SERIALIZER UPDATE v3: Inicio para instancia PK={instance.pk} ---")
        print(f"--- DEBUG SERIALIZER UPDATE v3: user recibido explícitamente: {user} (ID: {getattr(user, 'pk', 'N/A')}) ---")
        # Ya no necesitamos obtenerlo del contexto ni popearlo de validated_data
        print(f"--- DEBUG SERIALIZER UPDATE v3: validated_data recibida: {validated_data} ---")

        # ... (lógica de update como antes para modificar la instancia) ...
        audit_fields = {'created_at', 'created_by', 'modified_at', 'modified_by', 'deleted_at', 'deleted_by', 'status'}
        has_other_changes = False
        for attr, value in validated_data.items():
            if attr not in audit_fields:
                if getattr(instance, attr) != value:
                    setattr(instance, attr, value)
                    has_other_changes = True
        new_status = validated_data.get('status', None)
        status_changed = False
        if new_status is False and instance.status is True: # Soft deleting
            instance.status = False; instance.deleted_at = timezone.now(); instance.deleted_by = user; status_changed = True
        elif new_status is True and instance.status is False: # Reactivating
            instance.status = True; instance.deleted_at = None; instance.deleted_by = None; status_changed = True
        made_modification = status_changed or has_other_changes
        if made_modification: print(f"Updating instance {instance.pk} modified by user {user.pk if user else 'None'}")

        try:
            print(f"--- DEBUG SERIALIZER UPDATE v3: Llamando a instance.save(user={user}) ---")
            # Llama al save() de BaseModel pasando el user recibido
            instance.save(user=user)
            print(f"--- DEBUG SERIALIZER UPDATE v3: instance.save() completado. Instancia final: {instance} ---")
        except DjangoValidationError as e:
            print(f"--- ERROR SERIALIZER UPDATE v3: DjangoValidationError: {e} ---")
            raise serializers.ValidationError(e.detail)
        except Exception as e:
            print(f"--- ERROR SERIALIZER UPDATE v3: Exception: {e} ---")
            raise serializers.ValidationError(f"Error inesperado al guardar: {e}")

        print(f"--- DEBUG SERIALIZER UPDATE v3: Fin ---")
        return instance

    # --- Método TO_REPRESENTATION ---
    def to_representation(self, instance):
        # ... (como antes) ...
        representation = super().to_representation(instance)
        representation['created_by'] = instance.created_by.username if instance.created_by else None
        representation['modified_by'] = instance.modified_by.username if instance.modified_by else None
        representation['deleted_by'] = instance.deleted_by.username if instance.deleted_by else None
        representation.pop('created_by_username', None)
        representation.pop('modified_by_username', None)
        representation.pop('deleted_by_username', None)
        return representation
