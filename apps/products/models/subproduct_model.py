from django.db import models
from django.utils import timezone
from django.db.models import Sum
from apps.products.models.base_model import BaseModel

class Subproduct(BaseModel):
    """Modelo de Subproducto con atributos específicos para cables."""

    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(max_length=500, null=True, blank=True)
    status = models.BooleanField(default=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    number_coil = models.PositiveIntegerField(null=True, blank=True)
    initial_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coil_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    technical_sheet_photo = models.ImageField(upload_to='technical_sheets/', null=True, blank=True)
    
    # Relación con el producto padre
    parent = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='subproducts')
    
    
    def delete(self, *args, **kwargs):
        """Realiza un soft delete en lugar de eliminar el subproducto."""
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

        # Marcar stocks asociados como inactivos
        self.stocks.update(status=False, deleted_at=timezone.now())

    def __str__(self):
        return f'{self.parent.name} "SUBPRODUCTO"'

    @property
    def total_stock(self):
        """Calcula el stock total del subproducto sumando todas sus instancias de stock."""
        return self.stocks.aggregate(total=Sum('quantity'))['total'] or 0

    def update_stock(self, quantity_change, user, location=None):
        """Actualiza el stock del subproducto y registra un evento de movimiento."""
        if not self.stocks.exists():
            raise ValueError("El subproducto no tiene stock asignado.")

        # Importar StockEvent de manera local dentro de la función
        from apps.stocks.models.stock_event_model import StockEvent

        # Actualiza todos los stocks relacionados con el subproducto
        for stock in self.stocks.all():
            stock.update_stock(quantity_change, user, location)

            # Registrar un evento de stock por cada instancia de stock actualizada
            StockEvent.objects.create(
                stock_instance=stock,
                quantity_change=quantity_change,
                user=user,
                location=location
            )
