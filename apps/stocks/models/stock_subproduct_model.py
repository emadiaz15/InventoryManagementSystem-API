from django.db import models
from django.contrib.auth import get_user_model
from django.apps import apps
from .stock_product_model import ProductStock
from apps.stocks.models import BaseStock

User = get_user_model()

class SubproductStock(BaseStock):
    """Modelo para manejar el stock de subproductos y validar que su suma no supere el stock total del producto."""

    # Usamos apps.get_model() para evitar la importación circular
    stock_event = models.ForeignKey('stocks.StockEvent', on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        """Valida que la suma del stock de los subproductos no supere el stock total del producto."""
        # Se puede usar apps.get_model para obtener el modelo ProductStock
        if self.product_stock:
            total_subproduct_stock = sum(
                sp.quantity for sp in self.product_stock.subproduct_stocks.exclude(id=self.id)
            )
            if total_subproduct_stock + self.quantity > self.product_stock.quantity:
                raise ValueError("La suma del stock de los subproductos no puede superar el stock total del producto.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Stock de {self.subproduct.name}: {self.quantity}"

