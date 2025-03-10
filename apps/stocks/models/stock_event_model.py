from django.db import models
from django.contrib.auth import get_user_model
from apps.stocks.models import BaseStock  # Este es el modelo abstracto

User = get_user_model()

# Modelo concreto que hereda de BaseStock
class ConcreteStock(BaseStock):
    """Modelo concreto que hereda de BaseStock para usar en relaciones."""
    name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return self.name


class StockEvent(models.Model):
    """Registra cambios en el stock de productos y subproductos."""
    stock_instance = models.ForeignKey(
        ConcreteStock,  # Cambiado a ConcreteStock, ya no a BaseStock
        related_name='events',
        on_delete=models.CASCADE
    )
    quantity_change = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        help_text="Cantidad de cambio en stock."
    )
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('entrada', 'Entrada'),
            ('salida', 'Salida'),
            ('ajuste', 'Ajuste'),
        ],
        help_text="Tipo de evento de stock."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="stock_events",
        null=True,
        blank=True
    )
    location = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        """Asigna automáticamente el tipo de evento basado en el cambio de stock."""
        if self.quantity_change > 0:
            self.event_type = 'entrada'
        elif self.quantity_change < 0:
            self.event_type = 'salida'
        else:
            self.event_type = 'ajuste'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.event_type.capitalize()} de {self.quantity_change} unidades"
