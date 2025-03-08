from django.contrib.auth import get_user_model
from django.db import models


from apps.stocks.models.stock_event_model import StockEvent

User = get_user_model()

class Stock(models.Model):
    """Modelo para gestionar el stock de productos y subproductos."""
    
    quantity = models.DecimalField(max_digits=15, decimal_places=2, help_text="Cantidad actual de stock.")
    location = models.CharField(max_length=100, null=True, blank=True, help_text="Almacén o ubicación del stock (opcional).")

    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="stock_created", null=True, blank=True
    )  # Usuario que creó el stock
    modified_at = models.DateTimeField(null=True, blank=True)  # Fecha de modificación
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="stock_modified", null=True, blank=True
    )  # Usuario que modificó el stock

    def update_stock(self, quantity_change, user, location=None):
        """Método para actualizar la cantidad de stock, registrando un evento de movimiento."""
        if quantity_change == 0:
            return
        
        # Ajustar la cantidad de stock
        self.quantity += quantity_change

        # Si se proporciona una nueva ubicación, actualizarla
        if location:
            self.location = location
        
        # Actualizar la fecha y el usuario de la modificación
        self.modified_at = models.DateTimeField(auto_now=True)
        self.modified_by = user
        
        # Guardar los cambios
        self.save()

        # Registrar el movimiento de stock
        StockEvent.objects.create(
            stock=self,
            quantity_change=quantity_change,
            user=user,
            location=self.location
        )

    def __str__(self):
        return f"Stock {self.id} - {self.quantity} unidades"