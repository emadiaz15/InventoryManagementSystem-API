from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.stocks.models import BaseStock  # Asegúrate de que 'BaseStock' está bien importado

User = get_user_model()

# Modelo concreto que hereda de BaseStock
class ConcreteStock(BaseStock):
    """Modelo concreto que hereda de BaseStock para usar en relaciones con productos y subproductos."""
    name = models.CharField(max_length=255, help_text="Nombre del stock.")
    quantity = models.DecimalField(max_digits=15, decimal_places=2, help_text="Cantidad total del stock")

    def __str__(self):
        return self.name


class StockEvent(models.Model):
    """Registra cambios en el stock de productos y subproductos, y maneja eventos de stock como entrada, salida o ajuste."""
    stock_instance = models.ForeignKey(
        ConcreteStock,  # Asocia el evento con una instancia de ConcreteStock
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
        choices=[('entrada', 'Entrada'), ('salida', 'Salida'), ('ajuste', 'Ajuste')],
        help_text="Tipo de evento de stock."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora en que se crea el evento.")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="stock_events",
        null=True,
        blank=True
    )
    location = models.CharField(max_length=100, null=True, blank=True, help_text="Ubicación del stock.")

    def save(self, *args, **kwargs):
        """Asigna automáticamente el tipo de evento y realiza validaciones antes de guardar."""
        # No permitir cambios en stock que resulten en una cantidad negativa
        if self.quantity_change == 0:
            raise ValidationError("La cantidad de cambio no puede ser cero.")
        
        # Verificar si la cantidad total de stock va a ser negativa
        if self.stock_instance.quantity + self.quantity_change < 0:
            raise ValidationError("No puede haber un stock negativo.")

        # Determinar el tipo de evento de acuerdo con la cantidad de cambio
        if self.quantity_change > 0:
            self.event_type = 'entrada'
        elif self.quantity_change < 0:
            self.event_type = 'salida'
        else:
            self.event_type = 'ajuste'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.event_type.capitalize()} de {self.quantity_change} unidades en {self.location if self.location else 'ubicación desconocida'}"

