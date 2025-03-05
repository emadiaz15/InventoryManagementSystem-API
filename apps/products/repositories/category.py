from django.utils import timezone
from apps.products.models import Category

class CategoryRepository:
    @staticmethod
    def get_category_by_id(category_id: int):
        """
        Recupera una categoría por su ID, solo si está activa.
        """
        try:
            return Category.objects.get(id=category_id, status=True)
        except Category.DoesNotExist:
            return None

    @staticmethod
    def list_active_categories():
        """
        Retorna todas las categorías que están activas.
        """
        return Category.objects.filter(status=True)

    @staticmethod
    def create_category(name: str, description: str, user):
        """
        Crea una nueva categoría con el nombre, descripción y usuario dados.
        """
        category = Category(name=name, description=description, user=user)
        category.save()
        return category

    @staticmethod
    def update_category(category: Category, name: str = None, description: str = None):
        """
        Actualiza la información de una categoría existente.
        """
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        category.modified_at = timezone.now()
        category.save(update_fields=['name', 'description', 'modified_at'])
        return category

    @staticmethod
    def soft_delete(category: Category):
        """
        Realiza un soft delete en la categoría, estableciendo status en False y actualizando deleted_at.
        """
        category.status = False
        category.deleted_at = timezone.now()
        category.save(update_fields=['status', 'deleted_at'])
        return category
