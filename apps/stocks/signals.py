from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.products.models import Product, Subproduct
from apps.stocks.models.stock_product_model import ProductStock
from apps.stocks.models.stock_subproduct_model import SubproductStock

# Crear o actualizar el stock de productos cuando se guarda un producto
@receiver(post_save, sender=Product)
def create_or_update_stock_product(sender, instance, created, **kwargs):
    if created:  # Si el producto es recién creado
        # Crear el stock de producto con un valor inicial de quantity, por ejemplo, 0
        ProductStock.objects.create(product=instance, quantity=instance.quantity or 0)
    else:  # Si el producto ya existe y se actualiza
        try:
            stock_product = ProductStock.objects.get(product=instance)
            # Solo actualizar si el stock ha cambiado
            if stock_product.quantity != instance.quantity:
                stock_product.quantity = instance.quantity
                stock_product.save()
        except ProductStock.DoesNotExist:
            # Si no existe, crear uno nuevo
            ProductStock.objects.create(product=instance, quantity=instance.quantity or 0)

# Crear o actualizar el stock de subproductos cuando se guarda un subproducto
@receiver(post_save, sender=Subproduct)
def create_or_update_stock_subproduct(sender, instance, created, **kwargs):
    if created:  # Si el subproducto es recién creado
        # Crear el stock de subproducto con un valor inicial de quantity, por ejemplo, 0
        SubproductStock.objects.create(subproduct=instance, quantity=instance.quantity or 0)
    else:  # Si el subproducto ya existe y se actualiza
        try:
            stock_subproduct = SubproductStock.objects.get(subproduct=instance)
            # Solo actualizar si el stock ha cambiado
            if stock_subproduct.quantity != instance.quantity:
                stock_subproduct.quantity = instance.quantity
                stock_subproduct.save()
        except SubproductStock.DoesNotExist:
            # Si no existe, crear uno nuevo
            SubproductStock.objects.create(subproduct=instance, quantity=instance.quantity or 0)
