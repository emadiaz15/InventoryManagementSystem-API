from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.models import ProductStock, SubproductStock
from django.contrib.auth import get_user_model


@receiver(post_save, sender=Subproduct)
def sync_stock_for_subproduct(sender, instance, created, **kwargs):
    """
    Cada vez que se crea o actualiza un Subproduct, se ajusta el stock del Product relacionado.
    - Si es nuevo, se crea un Stock si no existe.
    - Si ya existe, se actualiza la cantidad total sumando los subproductos.
    """
    product = instance.parent  # Producto padre del Subproduct

    if not product:
        return  # Si no hay producto padre, no hacemos nada

    # Obtener usuario predeterminado (el primer staff disponible o cualquier usuario)
    User = get_user_model()
    default_user = User.objects.filter(is_staff=True).first() or User.objects.first()

    # ✅ Obtener el stock del producto padre
    product_stock, created_stock = ProductStock.objects.get_or_create(
        product=product,
        defaults={'quantity': 0, 'created_by': default_user}
    )

    # ✅ Obtener o crear el stock del subproducto
    subproduct_stock, created_sub_stock = SubproductStock.objects.get_or_create(
        subproduct=instance,
        defaults={'quantity': instance.initial_length or 0, 'created_by': default_user}
    )

    # ✅ Si el subproducto ya tenía stock, actualizamos la cantidad
    if not created_sub_stock:
        subproduct_stock.quantity = instance.initial_length or 0
        subproduct_stock.modified_by = default_user
        subproduct_stock.save()

    # ✅ Recalcular el stock total de subproductos activos relacionados
    subproducts = Subproduct.objects.filter(parent=product, status=True)
    total_subproduct_stock = sum(
        subproduct.stock.quantity for subproduct in subproducts if subproduct.stock
    )

    # ✅ Actualizar la cantidad total del stock del producto con la suma de los subproductos
    product_stock.quantity = total_subproduct_stock
    product_stock.modified_by = default_user
    product_stock.save()


@receiver(post_delete, sender=Subproduct)
def remove_stock_for_deleted_subproduct(sender, instance, **kwargs):
    """
    Cuando se elimina un Subproduct, se ajusta el stock del Product relacionado.
    """
    product = instance.parent  # Producto padre del Subproduct

    if not product:
        return  # Si no hay producto padre, no hacemos nada

    # ✅ Si el subproducto tenía stock, eliminarlo
    if instance.stock:
        instance.stock.delete()

    # ✅ Obtener usuario predeterminado
    User = get_user_model()
    default_user = User.objects.filter(is_staff=True).first() or User.objects.first()

    # ✅ Recalcular el stock total del producto padre
    subproducts = Subproduct.objects.filter(parent=product, status=True)
    total_subproduct_stock = sum(
        subproduct.stock.quantity for subproduct in subproducts if subproduct.stock
    )

    # ✅ Actualizar el stock del producto padre
    product_stock = ProductStock.objects.filter(product=product).first()
    if product_stock:
        product_stock.quantity = total_subproduct_stock
        product_stock.modified_by = default_user
        product_stock.save()
