from django.db import transaction
from django.utils import timezone
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from typing import Optional, List

class SubproductRepository:
    """Repositorio para manejar las operaciones de Subproduct."""

    @staticmethod
    def get_by_id(subproduct_id: int) -> Optional[Subproduct]:
        """
        Recupera un subproducto por su ID si está activo, retorna None si no existe.
        """
        return Subproduct.objects.filter(id=subproduct_id, status=True).first()

    @staticmethod
    def get_all_active(parent_product_id: int) -> List[Subproduct]:
        """
        Recupera todos los subproductos activos de un producto padre.
        """
        return Subproduct.objects.filter(parent_id=parent_product_id, status=True)

    @staticmethod
    def create(name: str, description: str, parent: Product, user, quantity: float, 
               brand: str, number_coil: str, initial_length: float, final_length: float, 
               total_weight: float, coil_weight: float) -> Subproduct:
        """
        Crea un nuevo subproducto asociado a un producto padre.
        """
        # Validación de tipo de parámetro 'parent'
        if not isinstance(parent, Product):
            raise ValueError("El parámetro 'parent' debe ser una instancia de Product.")

        # Validación de estado del producto padre
        if not parent.status:
            raise ValueError("El producto padre no está activo.")

        # Validaciones adicionales
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        if not name:
            raise ValueError("El nombre del subproducto es obligatorio.")

        # Obtener todos los subproductos asociados al producto padre
        subproducts = Subproduct.objects.filter(parent=parent)  # Usamos 'parent' en lugar de 'product'

        print("Subproductos asociados al producto padre:", subproducts)  # Depuración, opcional

        # Transacción atómica para crear el subproducto
        with transaction.atomic():
            subproduct = Subproduct(
                name=name,
                description=description,
                parent=parent,  # El 'parent' viene directamente desde la vista
                created_by=user,
                modified_by=user,
                quantity=quantity,
                brand=brand,
                number_coil=number_coil,
                initial_length=initial_length,
                final_length=final_length,
                total_weight=total_weight,
                coil_weight=coil_weight,
            )
            subproduct.save()

        return subproduct

    @staticmethod
    def update(subproduct_instance: Subproduct, user=None, **validated_data) -> Subproduct:
        """
        Actualiza un subproducto existente con los cambios proporcionados.
        Acepta un diccionario de datos validados para actualizar cualquier campo.
        """
        changes_made = False

        # Iteramos sobre los campos que vienen en validated_data y actualizamos los campos correspondientes
        for field, value in validated_data.items():
            if hasattr(subproduct_instance, field) and getattr(subproduct_instance, field) != value:
                setattr(subproduct_instance, field, value)
                changes_made = True

        # Si hubo cambios, asignamos los campos de fecha y usuario
        if changes_made:
            subproduct_instance.modified_at = timezone.now()

            # Si 'user' está presente, actualizamos los campos de auditoría
            if user:
                subproduct_instance.modified_by = user  # Asignar el usuario que realizó la modificación

            subproduct_instance.save()

        return subproduct_instance


    @staticmethod
    def soft_delete(subproduct_instance: Subproduct, user) -> Subproduct:
        """
        Realiza un soft delete, estableciendo `status=False`.
        """
        subproduct_instance.status = False
        subproduct_instance.deleted_at = timezone.now()
        subproduct_instance.deleted_by = user
        subproduct_instance.save(update_fields=['status', 'deleted_at', 'deleted_by'])

        return subproduct_instance
