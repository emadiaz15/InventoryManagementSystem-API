from django.utils import timezone
from apps.products.models.type_model import Type

class TypeRepository:
    @staticmethod
    def get_by_id(type_id: int):
        """
        Recupera un tipo de producto por su ID.
        """
        try:
            return Type.objects.get(id=type_id, status=True)
        except Type.DoesNotExist:
            return None

    @staticmethod
    def get_all_active():
        """
        Retorna todos los tipos activos.
        """
        return Type.objects.filter(status=True)

    @staticmethod
    def create(name: str, description: str, category_id: int, user):
        """
        Crea un nuevo tipo de producto.
        """
        type_instance = Type(name=name, description=description, category_id=category_id)
        type_instance.save(user=user)
        return type_instance

    @staticmethod
    def update(type_instance: Type, name: str = None, description: str = None, status: bool = None, user=None):
        """
        Actualiza un tipo de producto.
        """
        changes_made = False
        if name is not None:
            type_instance.name = name
            changes_made = True
        if description is not None:
            type_instance.description = description
            changes_made = True
        if status is not None:
            type_instance.status = status
            changes_made = True
        if user:
            type_instance.modified_by = user
        if changes_made:
            type_instance.modified_at = timezone.now()
            type_instance.save(update_fields=['name', 'description', 'status', 'modified_at', 'deleted_at', 'modified_by'])
            
        return type_instance

    @staticmethod
    def soft_delete(type_instance: Type, user):
        """
        Realiza un soft delete en el tipo de producto.
        """
        type_instance.status = False
        type_instance.deleted_at = timezone.now()
        type_instance.deleted_by = user
        type_instance.save(user=user)

        return type_instance
