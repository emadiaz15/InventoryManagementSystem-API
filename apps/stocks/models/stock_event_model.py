from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.products.models.base_model import BaseModel

from apps.stocks.models.stock_product_model import ProductStock
from apps.stocks.models.stock_subproduct_model import SubproductStock

class StockEvent(BaseModel): # HEREDA DE BASEMODEL
    """Registra cada movimiento (entrada/salida/ajuste) de stock."""

    EVENT_TYPES = [
        ('ingreso', 'Ingreso'),
        ('egreso_venta', 'Egreso por Venta'),
        ('egreso_corte', 'Egreso por Corte'),
        ('egreso_ajuste', 'Egreso por Ajuste'),
        ('ingreso_ajuste', 'Ingreso por Ajuste'),
        ('traslado_salida', 'Salida por Traslado'),
        ('traslado_entrada', 'Entrada por Traslado'),
    ]

    # --- Relación al Stock afectado ---
    # Usamos FKs separadas a ProductStock y SubproductStock (más simple que GenericForeignKey)
    # Solo uno de estos dos debería tener valor para cada evento.
    product_stock = models.ForeignKey(
        ProductStock,
        on_delete=models.CASCADE, # O PROTECT si quieres mantener eventos si se borra el stock
        null=True, blank=True, # Puede ser nulo si el evento es de SubproductStock
        related_name='events',
        verbose_name="Stock de Producto Afectado"
    )
    subproduct_stock = models.ForeignKey(
        SubproductStock,
        on_delete=models.CASCADE, # O PROTECT
        null=True, blank=True, # Puede ser nulo si el evento es de ProductStock
        related_name='events',
        verbose_name="Stock de Subproducto Afectado"
    )

    # --- Detalles del Evento ---
    quantity_change = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Cambio en la cantidad (+ para entrada, - para salida)"
    )
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
        help_text="Tipo de evento de stock"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales") # Campo útil

    class Meta:
        verbose_name = "Evento de Stock"
        verbose_name_plural = "Eventos de Stock"
        ordering = ['-created_at'] # Mantenemos el orden por defecto aquí también

    def clean(self):
        """Validaciones a nivel de modelo para el evento."""
        super().clean()
        # Asegurar que solo uno de los FKs a stock esté asignado
        if self.product_stock and self.subproduct_stock:
            raise ValidationError("Un evento de stock solo puede pertenecer a un ProductStock O a un SubproductStock, no a ambos.")
        if not self.product_stock and not self.subproduct_stock:
             raise ValidationError("Un evento de stock debe estar asociado a un ProductStock o a un SubproductStock.")
        # No permitir cantidad de cambio cero
        if self.quantity_change == 0:
             raise ValidationError("La cantidad de cambio no puede ser cero.")

    def __str__(self):
        target = self.product_stock or self.subproduct_stock or "Stock Desconocido"
        op = "+" if self.quantity_change > 0 else ""
        return f"{self.get_event_type_display()}: {op}{self.quantity_change} para {target}"
