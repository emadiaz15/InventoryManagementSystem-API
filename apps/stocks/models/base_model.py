from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseStock(models.Model):
    """Modelo base para manejar stock y eventos de stock para productos y subproductos."""
    quantity = models.DecimalField(max_digits=15, decimal_places=2, help_text="Cantidad de stock.")
    location = models.CharField(max_length=100, null=True, blank=True, help_text="Ubicación del stock.")
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="%(class)s_created", null=True, blank=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="%(class)s_modified", null=True, blank=True)

    class Meta:
        abstract = True  # Esto asegura que no se cree una tabla para BaseStock, solo sirve de base.

    def update_stock(self, quantity_change, user, location=None):
        """Actualiza el stock y registra el evento en StockEvent."""
        from apps.stocks.models.stock_event_model import StockEvent
        if quantity_change == 0:
            return

        self.quantity += quantity_change
        if location:
            self.location = location

        self.modified_at = timezone.now()
        self.modified_by = user
        self.save()

        StockEvent.objects.create(
            stock_instance=self,
            quantity_change=quantity_change,
            user=user,
            location=self.location
        )

    def __str__(self):
        return f"Stock de {self.__class__.__name__}: {self.quantity}"
