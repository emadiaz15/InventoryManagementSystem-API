from django.utils import timezone
from apps.products.models import Category

class CategoryRepository:
    @staticmethod
    def get_by_id(category_id: int):
        """
        Recupera una categoría por su ID, solo si está activa.
        """
        try:
            return Category.objects.get(id=category_id, status=True)
        except Category.DoesNotExist:
            return None

    @staticmethod
    def get_all_active():
        """
        Retorna todas las categorías que están activas.
        """
        return Category.objects.filter(status=True)

    @staticmethod
    def create(name: str, description: str, user):
        """
        Crea una nueva categoría con el nombre, descripción y usuario dados.
        """
        category = Category(name=name, description=description, created_by=user)
        category.save()
        return category

    @staticmethod
    def update(category: Category, name: str = None, description: str = None, status: bool = None):
        """
        Actualiza la información de una categoría existente y guarda el campo deleted_at
        si se actualizan ciertos campos.
        """
        # Verificar si hay cambios en los campos
        changes_made = False
        if name is not None:
            category.name = name
            changes_made = True
        if description is not None:
            category.description = description
            changes_made = True
        if status is not None:
            category.status = status
            changes_made = True

        # Si hubo cambios, actualizar la fecha en deleted_at
        if changes_made:
            # Si el status cambia a 'false', guardamos la fecha de eliminación en 'deleted_at'
            if status is not None and status is False:
                category.deleted_at = timezone.now()  # Marca el tiempo de eliminación

            category.modified_at = timezone.now()  # Marca el tiempo de la última modificación
            category.save(update_fields=['name', 'description', 'status', 'modified_at', 'deleted_at'])

        return category

    @staticmethod
    def soft_delete(category: Category, user):
        """
        Realiza un soft delete en la categoría, estableciendo status en False y actualizando deleted_at.
        """
        category.status = False
        category.deleted_at = timezone.now()
        category.deleted_by = user
        category.save(update_fields=['status', 'deleted_at', 'deleted_by'])
        return category

    @staticmethod
    def get_all():
        """
        Retorna todas las categorías, activas o inactivas.
        """
        return Category.objects.all()
