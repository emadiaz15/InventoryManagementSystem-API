from django.db import models
from apps.stocks.models import BaseStock
from django.contrib.auth import get_user_model
from apps.stocks.models.stock_event_model import StockEvent
User = get_user_model()

class ProductStock(BaseStock):
    """Modelo para manejar el stock total de un producto."""
        
    stock_event = models.ForeignKey('stocks.StockEvent', on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Stock de {self.product.name}: {self.quantity}"

    # Método para hacer uso de 'Product' después de que haya sido importado
    def update_stock(self, quantity_change):
        """Lógica para actualizar el stock del producto"""
        product_instance = self.product
        product_instance.quantity += quantity_change
        product_instance.save()
