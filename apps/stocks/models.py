from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import F
from apps.products.models import Product

User = get_user_model()

class Stock(models.Model):
    """
    Modelo que representa el stock de un Product en el inventario.
    Maneja ubicaciones, soft-delete, y mantiene la trazabilidad a través de StockHistory.
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='stocks',
        help_text="Referencia al producto (puede ser producto raíz o subproducto)."
    )
    quantity = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Cantidad actual de stock."
    )
    location = models.CharField(
        max_length=100, null=True, blank=True,
        help_text="Almacén o ubicación del stock (opcional)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Fecha y hora de la creación del registro."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Fecha y hora de la última modificación."
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="Usuario que realizó el ajuste de stock."
    )
    is_active = models.BooleanField(
        default=True, help_text="Indica si el stock está activo (eliminación suave)."
    )

    def __str__(self):
        return f"Stock for {self.product.name} at {self.location or 'Default'} (Updated: {self.updated_at})"

    def clean(self):
        """
        Evita que la cantidad sea negativa en cualquier circunstancia.
        Se llama automáticamente en .save() si no se deshabilita la validación.
        """
        if self.quantity < 0:
            raise ValidationError("Stock quantity cannot be negative.")

    @transaction.atomic
    def apply_change(self, delta, reason, user):
        """
        Aplica un cambio (+/-) a la cantidad de stock de manera concurrente.
        
        :param delta: decimal positivo (para aumentar) o negativo (para disminuir).
        :param reason: motivo del ajuste.
        :param user: usuario que realiza el ajuste.
        :raises ValueError: si el resultado quedara negativo.
        """
        # Bloqueamos la fila actual para evitar condiciones de carrera en entornos concurrentes
        stock_refreshed = Stock.objects.select_for_update().get(pk=self.pk)

        stock_before = stock_refreshed.quantity
        new_quantity = stock_before + delta

        if new_quantity < 0:
            raise ValueError("The change results in a negative quantity, which is not allowed.")

        stock_refreshed.quantity = new_quantity
        stock_refreshed.save()

        # Registrar el cambio en el historial
        StockHistory.objects.create(
            product=self.product,
            stock_before=stock_before,
            stock_after=new_quantity,
            change_reason=reason,
            user=user
        )

    def soft_delete(self, reason, user):
        """
        Elimina de manera suave el stock marcando el campo `is_active` como False
        y lleva la cantidad a 0. Registra el cambio en el historial (StockHistory).
        """
        stock_before = self.quantity
        self.is_active = False
        self.quantity = 0
        self.save()
        StockHistory.objects.create(
            product=self.product,
            stock_before=stock_before,
            stock_after=0,
            change_reason=reason or "Soft deletion of stock",
            user=user
        )

    @staticmethod
    def get_total_stock():
        """
        Calcula la suma global de stock activo en el sistema (todos los productos).
        Si deseas el stock total de un producto en particular, filtra con .filter(product=...).
        """
        total_stock = Stock.objects.filter(is_active=True).aggregate(
            total_quantity=models.Sum('quantity')
        )['total_quantity'] or 0
        return total_stock


class StockHistory(models.Model):
    """
    Modelo que representa el historial de cambios de stock.
    Registra ajustes tanto en productos padre como en subproductos (ya que es el mismo modelo Product).
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='stock_history',
        null=True, blank=True,
        help_text="Producto al que se asocia el ajuste de stock."
    )
    stock_before = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Cantidad de stock antes del ajuste."
    )
    stock_after = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Cantidad de stock después del ajuste."
    )
    change_reason = models.TextField(
        help_text="Motivo del ajuste de stock.", null=True, blank=True
    )
    recorded_at = models.DateTimeField(
        auto_now_add=True, help_text="Fecha y hora del ajuste de stock."
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="Usuario que realizó el ajuste."
    )

    def __str__(self):
        if self.product:
            return f"History for {self.product.name} - Change at {self.recorded_at}"
        return f"History record at {self.recorded_at}"
