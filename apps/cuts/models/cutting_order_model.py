from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.users.models import User
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.models import SubproductStock
from .base_model import BaseModel
from apps.stocks.models import StockEvent

class CuttingOrder(BaseModel):
    """
    Modelo para manejar las órdenes de corte de cable, utilizando la lógica de BaseModel.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_process', 'In Process'),
        ('completed', 'Completed'),
    )

    subproduct = models.ForeignKey(
        Subproduct, null=True, blank=True, on_delete=models.SET_NULL, related_name='cutting_orders'
    )
    customer = models.CharField(max_length=255, help_text="Customer for whom the cutting order is made")
    cutting_quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Quantity to cut in meters")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_by = models.ForeignKey(User, related_name='assigned_cutting_orders', on_delete=models.SET_NULL, null=True)
    assigned_to = models.ForeignKey(User, related_name='cutting_orders', on_delete=models.SET_NULL, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Cutting Order {self.pk} for {self.customer} - Status: {self.status}'

    def clean(self):
        """
        Validaciones personalizadas:
        1. El subproducto no puede ser nulo.
        2. Verifica si hay suficiente stock disponible para cortar.
        """
        if not self.subproduct:
            raise ValidationError("A subproduct must be selected for the cutting order.")
        
        # Cambia esta línea para acceder al stock de SubproductStock
        try:
            stock = SubproductStock.objects.filter(subproduct=self.subproduct).latest('created_at')
        except SubproductStock.DoesNotExist:
            raise ValidationError(f"No stock available for subproduct {self.subproduct.name}.")

        if self.cutting_quantity > stock.quantity:
            raise ValidationError(f"Insufficient stock for subproduct {self.subproduct.name}. Available: {stock.quantity}")


    def save(self, *args, **kwargs):
        """
        Sobrescribe el método `save` para incluir validaciones y asignación de usuario.
        """
        self.clean()

        # Asegúrate de que el 'user' se pase correctamente a través del serializer o la vista.
        if not self.assigned_by:
            raise ValidationError("Assigned by user must be provided.")

        # Llamamos al método `save` de la clase base
        super().save(*args, **kwargs)

    def complete_cutting(self):
        """
        Completa la orden de corte, restando la cantidad cortada del stock.
        """
        if self.status != 'in_process':
            raise ValidationError("The order must be in 'in_process' status to complete.")

        try:
            stock = self.subproduct.stocks.latest('created_at')
        except SubproductStock.DoesNotExist:
            raise ValidationError(f"No stock available for subproduct {self.subproduct.name}.")

        if self.cutting_quantity > stock.quantity:
            raise ValidationError(f"Not enough stock to complete the order.")

        # Descontamos la cantidad de stock
        stock.quantity -= self.cutting_quantity
        stock.save()

        # Crear el evento de stock
        StockEvent.objects.create(
            stock_instance=stock,
            quantity_change=-self.cutting_quantity,
            event_type='salida',  # Movimiento de salida al completar la orden
            user=self.assigned_by,  # Asignar el usuario que está completando la orden
            location=stock.location
        )

        # Actualizar el estado de la orden
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("can_assign_cutting_order", "Can assign cutting orders"),
            ("can_process_cutting_order", "Can process cutting orders"),
        ]
