from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product

User = get_user_model()

class Stock(models.Model):
    """
    Modelo que representa el stock de un Product en el inventario.
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='stocks',
        help_text="Referencia al producto (puede ser producto raíz o subproducto)."
    )
    quantity = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Cantidad actual de stock."
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
        # Muestra el nombre del producto y la fecha de actualización del stock.
        # Mensaje en inglés:
        return f"Stock for {self.product.name} on {self.updated_at}"

    def update_stock(self, cut_length, reason, user):
        """
        Actualiza el stock al realizar un ajuste de longitud (cut_length).
        Registra el cambio en el historial (StockHistory).
        """
        stock_before = self.quantity
        new_quantity = stock_before - cut_length

        if new_quantity < 0:
            # Mensaje en inglés:
            raise ValueError("The cut exceeds the available stock length.")

        self.quantity = new_quantity
        self.save()
        StockHistory.objects.create(
            product=self.product,
            stock_before=stock_before,
            stock_after=new_quantity,
            change_reason=reason,
            user=user
        )

    def soft_delete(self, reason, user):
        """
        Elimina de manera suave el stock marcando el campo `is_active` como False.
        Registra el cambio en el historial (StockHistory).
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
        Calcula el stock total sumando las cantidades de stock de todos los `Product` activos.
        """
        total_stock = Stock.objects.filter(is_active=True).aggregate(
            total_quantity=models.Sum('quantity')
        )['total_quantity'] or 0
        return total_stock


class StockHistory(models.Model):
    """
    Modelo que representa el historial de cambios de stock.
    Registra ajustes tanto en productos raíz como en subproductos (simplemente
    otro Product con parent asignado).
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='stock_history',
        null=True, blank=True,
        help_text="Producto al que se asocia el ajuste de stock."
    )
    stock_before = models.DecimalField(
        max_digits=15, decimal_places=2, help_text="Cantidad de stock antes del ajuste."
    )
    stock_after = models.DecimalField(
        max_digits=15, decimal_places=2, help_text="Cantidad de stock después del ajuste."
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
        # Muestra información del producto y la fecha del ajuste.
        # Mensaje en inglés:
        if self.product is not None:
            return f"History for {self.product.name} - Change at {self.recorded_at}"
        return f"History record at {self.recorded_at}"
