from django.db import models
from django.contrib.auth import get_user_model
from apps.stocks.models import BaseStock
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.models import ProductStock

User = get_user_model()

class SubproductStock(BaseStock):
    """Modelo para manejar el stock de subproductos y validar que su suma no supere el stock total del producto."""

    subproduct = models.ForeignKey(Subproduct, on_delete=models.CASCADE, related_name='subproduct_stocks', null=True)
    stock_event = models.ForeignKey('stocks.StockEvent', on_delete=models.CASCADE)
    product_stock = models.ForeignKey(ProductStock, on_delete=models.CASCADE, related_name='subproduct_stocks')  # Relación agregada
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """Valida que la suma del stock de los subproductos no supere el stock total del producto."""
        if self.product_stock:  # Aseguramos que la relación con ProductStock esté presente
            total_subproduct_stock = sum(
                sp.quantity for sp in self.product_stock.subproduct_stocks.exclude(id=self.id)
            )
            if total_subproduct_stock + self.quantity > self.product_stock.quantity:
                raise ValueError("La suma del stock de los subproductos no puede superar el stock total del producto.")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Stock de {self.subproduct.name}: {self.quantity}"
