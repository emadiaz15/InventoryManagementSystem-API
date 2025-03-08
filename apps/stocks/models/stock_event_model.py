from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class StockEvent(models.Model):
    """Modelo para registrar los movimientos de stock (entradas, salidas, ajustes)."""
    
    # Referencia al modelo Stock usando el formato correcto
    stock = models.ForeignKey('stocks.Stock', related_name='events', on_delete=models.CASCADE)
    quantity_change = models.DecimalField(max_digits=15, decimal_places=2, help_text="Cantidad que se ajusta (positiva para entradas, negativa para salidas).")
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('entrada', 'Entrada'),
            ('salida', 'Salida'),
            ('ajuste', 'Ajuste'),
        ],
        help_text="Tipo de evento de stock (Entrada, Salida, Ajuste)"
    )

    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="stock_events", null=True, blank=True
    )  # Usuario que realizó el evento
    modified_at = models.DateTimeField(null=True, blank=True)  # Fecha de modificación
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="stock_events_modified", null=True, blank=True
    )  # Usuario que modificó el evento

    def save(self, *args, **kwargs):
        """Método personalizado para guardar el evento."""
        if self.quantity_change > 0:
            self.event_type = 'entrada'
        elif self.quantity_change < 0:
            self.event_type = 'salida'
        else:
            self.event_type = 'ajuste'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Evento de stock {self.id} - {self.event_type} de {self.quantity_change} unidades"
