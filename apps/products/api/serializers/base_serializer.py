from rest_framework import serializers
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
import logging

User = get_user_model()

logger = logging.getLogger(__name__)

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
        if isinstance(value, str):
            return value.strip().lower().replace(" ", "")
        return value

    def _get_normalized_name(self, name):
        if not isinstance(name, str):
            raise serializers.ValidationError("El nombre debe ser texto.")
        if not hasattr(self.Meta, 'model') or not hasattr(self.Meta.model, 'name'):
            return name
        normalized_name = self._normalize_field(name)
        ModelClass = self.Meta.model
        query = Q(name__iexact=normalized_name)
        instance_pk = getattr(self.instance, 'pk', None)
        if instance_pk:
            query &= ~Q(pk=instance_pk)
        if ModelClass.objects.filter(query).exists():
            raise serializers.ValidationError(f"El nombre '{name}' ya existe.")
        return name

    def _validate_unique_code(self, code):
        if not hasattr(self.Meta, 'model') or not hasattr(self.Meta.model, 'code'):
            return
        ModelClass = self.Meta.model
        query = Q(code=code)
        instance_pk = getattr(self.instance, 'pk', None)
        if instance_pk:
            query &= ~Q(pk=instance_pk)
        if ModelClass.objects.filter(query).exists():
            raise serializers.ValidationError(f"El código '{code}' ya existe.")

    def _filter_validated_data(self, validated_data):
        """
        Devuelve un diccionario que incluya solo las claves que correspondan a
        campos reales definidos en el modelo (se omiten los campos write-only u otros
        que no estén presentes en el modelo).
        """
        # Obtener los nombres de los campos reales (tomados de _meta.fields)
        model_field_names = {field.name for field in self.Meta.model._meta.get_fields() if hasattr(field, 'attname')}
        return {k: v for k, v in validated_data.items() if k in model_field_names}

    def save(self, **kwargs):
        """
        Extrae 'user' de kwargs, filtra los datos validados para dejar solo los campos reales
        del modelo y llama a create/update pasándole 'user'.
        """
        user = kwargs.pop('user', None)  # Extrae user de save(user=...)
        if user:
            self.context['user'] = user
        if 'request' not in self.context and user and hasattr(user, '_request'):
            self.context['request'] = getattr(user, '_request')

        # Validar datos primero
        assert hasattr(self, '_validated_data'), (
            'Cannot call `.save()` before `.is_valid()` has been called.'
        )
        validated_data = dict(self._validated_data)
        # Filtrar datos para que solo incluyan campos definidos en el modelo
        validated_data = self._filter_validated_data(validated_data)

        try:
            if self.instance is not None:
                self.instance = self.update(self.instance, validated_data, user=user)
                assert self.instance is not None, (
                    '`update()` did not return an object instance.'
                )
            else:
                self.instance = self.create(validated_data, user=user)
                assert self.instance is not None, (
                    '`create()` did not return an object instance.'
                )
        except (TypeError, ValueError, DjangoValidationError) as exc:
            raise serializers.ValidationError(detail=serializers.as_serializer_error(exc))
        return self.instance

    def create(self, validated_data, user=None):
        """
        Maneja la creación, usando el 'user' recibido explícitamente.
        """
        logger.info("--- DEBUG SERIALIZER CREATE v3: Inicio ---")
        logger.info(
            f"--- DEBUG SERIALIZER CREATE v3: user recibido: {user} (ID: {getattr(user, 'pk', 'N/A')}) ---"
        )
        logger.info(
            f"--- DEBUG SERIALIZER CREATE v3: validated_data: {validated_data} ---"
        )
        try:
            instance = self.Meta.model(**validated_data)
            logger.info(
                f"--- DEBUG SERIALIZER CREATE v3: Instancia creada en memoria: {instance} ---"
            )
            logger.info(
                f"--- DEBUG SERIALIZER CREATE v3: Llamando a instance.save(user={user}) ---"
            )
            instance.save(user=user)
            logger.info(
                f"--- DEBUG SERIALIZER CREATE v3: instance.save() completado. Instancia final: {instance} ---"
            )
        except TypeError as e:
            logger.error(f"--- ERROR SERIALIZER CREATE v3: TypeError: {e} ---")
            raise TypeError(f"Error al instanciar {self.Meta.model.__name__}: {e}")
        except DjangoValidationError as e:
            logger.error(
                f"--- ERROR SERIALIZER CREATE v3: DjangoValidationError: {e} ---"
            )
            raise serializers.ValidationError(e.detail)
        except Exception as e:
            logger.error(f"--- ERROR SERIALIZER CREATE v3: Exception: {e} ---")
            raise serializers.ValidationError(f"Error inesperado al guardar: {e}")
        logger.info("--- DEBUG SERIALIZER CREATE v3: Fin ---")
        return instance

    def update(self, instance, validated_data, user=None):
        """
        Maneja la actualización, usando el 'user' recibido explícitamente.
        """
        logger.info(
            f"--- DEBUG SERIALIZER UPDATE v3: Inicio para instancia PK={instance.pk} ---"
        )
        logger.info(
            f"--- DEBUG SERIALIZER UPDATE v3: user recibido: {user} (ID: {getattr(user, 'pk', 'N/A')}) ---"
        )
        logger.info(
            f"--- DEBUG SERIALIZER UPDATE v3: validated_data: {validated_data} ---"
        )
        validated_data = self._filter_validated_data(validated_data)
        audit_fields = {'created_at', 'created_by', 'modified_at', 'modified_by', 'deleted_at', 'deleted_by', 'status'}
        has_other_changes = False
        for attr, value in validated_data.items():
            if attr not in audit_fields and getattr(instance, attr) != value:
                setattr(instance, attr, value)
                has_other_changes = True
        new_status = validated_data.get('status', None)
        status_changed = False
        if new_status is False and instance.status is True:
            instance.status = False
            instance.deleted_at = timezone.now()
            instance.deleted_by = user
            status_changed = True
        elif new_status is True and instance.status is False:
            instance.status = True
            instance.deleted_at = None
            instance.deleted_by = None
            status_changed = True
        if status_changed or has_other_changes:
            logger.info(
                f"Updating instance {instance.pk} modified by user {user.pk if user else 'None'}"
            )
        try:
            logger.info(
                f"--- DEBUG SERIALIZER UPDATE v3: Llamando a instance.save(user={user}) ---"
            )
            instance.save(user=user)
            logger.info(
                f"--- DEBUG SERIALIZER UPDATE v3: instance.save() completado. Instancia final: {instance} ---"
            )
        except DjangoValidationError as e:
            logger.error(
                f"--- ERROR SERIALIZER UPDATE v3: DjangoValidationError: {e} ---"
            )
            raise serializers.ValidationError(e.detail)
        except Exception as e:
            logger.error(f"--- ERROR SERIALIZER UPDATE v3: Exception: {e} ---")
            raise serializers.ValidationError(f"Error inesperado al guardar: {e}")
        logger.info(f"--- DEBUG SERIALIZER UPDATE v3: Fin ---")
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = instance.created_by.username if instance.created_by else None
        representation['modified_by'] = instance.modified_by.username if instance.modified_by else None
        representation['deleted_by'] = instance.deleted_by.username if instance.deleted_by else None
        representation.pop('created_by_username', None)
        representation.pop('modified_by_username', None)
        representation.pop('deleted_by_username', None)
        return representation
