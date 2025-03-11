from django.db import models
from django.contrib.auth import get_user_model
from apps.stocks.models import BaseStock
from apps.stocks.models.stock_event_model import StockEvent
from apps.products.models import Product  # Asegúrate de importar el modelo Product correctamente.

User = get_user_model()

class ProductStock(BaseStock):
    """Modelo para manejar el stock total de un producto."""
    
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='product_stocks')
    stock_event = models.ForeignKey(StockEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_stocks')
    status = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Stock de {self.product.name}: {self.quantity}"

    def update_stock(self, quantity_change):
        """Lógica para actualizar el stock del producto"""
        # Actualizar la cantidad de stock del producto
        self.product.quantity += quantity_change
        self.product.save()

        # Crear un nuevo evento de stock para registrar el cambio
        StockEvent.objects.create(
            stock_instance=self,
            quantity_change=quantity_change,
            event_type="ajuste" if quantity_change == 0 else ("entrada" if quantity_change > 0 else "salida"),
            user=None,  # Asignar el usuario si es necesario
            location=self.product.location  # Si el producto tiene una ubicación asociada, puedes usarla.
        )

