# apps/stocks/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.products.models import CableAttributes
from apps.stocks.models import Stock

@receiver(post_save, sender=CableAttributes)
def create_stock_for_cable(sender, instance, created, **kwargs):
    """
    Cada vez que se crea un CableAttributes, se crea un registro de Stock 
    usando initial_length si no existe un Stock para ese producto.
    """
    if created:
        product = instance.parent  # El product al que CableAttributes está enlazado (OneToOne o ForeignKey)
        if instance.initial_length:
            # Verificamos si ya existe un Stock activo
            if not Stock.objects.filter(product=product, is_active=True).exists():
                from django.contrib.auth import get_user_model
                User = get_user_model()
                default_user = User.objects.filter(is_staff=True).first() or User.objects.first()

                Stock.objects.create(
                    product=product,
                    quantity=instance.initial_length,  # El valor de initial_length
                    user=default_user,
                    is_active=True
                )
