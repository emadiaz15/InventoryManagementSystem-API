from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from apps.products.models.type_model import Type
from apps.products.models.category_model import Category

class TypeRepository:
    """
    Repositorio para gestionar el acceso a datos del modelo Type.
    Delega la lógica de auditoría y soft delete a BaseModel.
    Utiliza el ordenamiento por defecto de BaseModel (-created_at).
    """

    @staticmethod
    def get_by_id(type_id: int) -> Type | None:
        """Recupera un tipo de producto activo por su ID."""
        try:
            return Type.objects.get(id=type_id, status=True)
        except Type.DoesNotExist:
            return None

    @staticmethod
    def get_all_active():
        """
        Retorna un QuerySet de todos los tipos activos.
        Ordenados por defecto por -created_at (de BaseModel.Meta).
        """
        # SIN .order_by('name') para usar el default de Meta
        return Type.objects.filter(status=True)

    # --- CREATE (Delega a save de BaseModel) ---
    @staticmethod
    def create(name: str, description: str, category_id: int, user) -> Type:
        """Crea un nuevo tipo de producto usando la lógica de BaseModel.save."""
        try:
            category_instance = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise ValueError(f"La categoría con ID {category_id} no existe.")

        type_instance = Type(
            name=name,
            description=description,
            category=category_instance
        )
        type_instance.save(user=user) # Delega auditoría a BaseModel
        return type_instance

    # --- UPDATE (Delega a save de BaseModel) ---
    @staticmethod
    def update(type_instance: Type, user, name: str = None, description: str = None, category_id: int = None) -> Type:
        """Actualiza un tipo usando la lógica de BaseModel.save."""
        changes_made = False
        if name is not None and type_instance.name != name:
            type_instance.name = name
            changes_made = True
        if description is not None and type_instance.description != description:
            type_instance.description = description
            changes_made = True
        if category_id is not None and type_instance.category_id != category_id:
            try:
                new_category_instance = Category.objects.get(pk=category_id)
                type_instance.category = new_category_instance
                changes_made = True
            except Category.DoesNotExist:
                 raise ValueError(f"La categoría con ID {category_id} no existe.")

        if changes_made:
            type_instance.save(user=user) # Delega auditoría a BaseModel
        return type_instance

    # --- SOFT DELETE (Delega a delete de BaseModel) ---
    @staticmethod
    def soft_delete(type_instance: Type, user) -> Type:
        """Realiza un soft delete usando la lógica de BaseModel.delete."""
        type_instance.delete(user=user) # Delega auditoría a BaseModel
        return type_instance
    