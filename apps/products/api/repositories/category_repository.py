from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from apps.products.models.category_model import Category

class CategoryRepository:
    """
    Repositorio para gestionar el acceso a datos del modelo Category.
    Delega la lógica de auditoría y soft delete a BaseModel.
    Utiliza el ordenamiento por defecto de BaseModel (-created_at).
    """

    @staticmethod
    def get_by_id(category_id: int) -> Category | None:
        """Recupera una categoría activa por su ID."""
        try:
            return Category.objects.get(id=category_id, status=True)
        except Category.DoesNotExist:
            return None

    @staticmethod
    def get_all_active():
        """
        Retorna un QuerySet de todas las categorías activas.
        Ordenadas por defecto por -created_at (de BaseModel.Meta).
        """
        # SIN .order_by('name') para usar el default de Meta
        return Category.objects.filter(status=True)


    # --- CREATE (Delega a save de BaseModel) ---
    @staticmethod
    def create(name: str, description: str, user) -> Category:
        """Crea una nueva categoría usando la lógica de BaseModel.save."""
        category_instance = Category(name=name, description=description)
        category_instance.save(user=user) # BaseModel.save() asigna created_by
        return category_instance

    # --- UPDATE (Delega a save de BaseModel) ---
    @staticmethod
    def update(category_instance: Category, user, name: str = None, description: str = None) -> Category:
        """Actualiza una categoría usando la lógica de BaseModel.save."""
        changes_made = False
        if name is not None and category_instance.name != name:
            category_instance.name = name
            changes_made = True
        if description is not None and category_instance.description != description:
            category_instance.description = description
            changes_made = True

        if changes_made:
            category_instance.save(user=user) # BaseModel.save() asigna modified_*
        return category_instance

    # --- SOFT DELETE (Delega a delete de BaseModel) ---
    @staticmethod
    def soft_delete(category_instance: Category, user) -> Category:
        """Realiza un soft delete usando la lógica de BaseModel.delete."""
        category_instance.delete(user=user) # BaseModel.delete() asigna deleted_* y status
        return category_instance
