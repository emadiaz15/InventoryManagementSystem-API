from django.db import models
from apps.products.models import Product
from apps.users.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import now

class CuttingOrder(models.Model):
    """
    Modelo que representa una orden de corte para productos.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_process', 'In Process'),
        ('completed', 'Completed'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cutting_orders')
    customer = models.CharField(max_length=255, help_text="Customer name for whom the cutting order is made")
    cutting_quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Quantity in meters to cut")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_cutting_orders')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cutting_operations')
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Cutting Order {self.pk} for {self.customer} - Status: {self.status}'

    def clean(self):
        """
        Validación personalizada para asegurarse de que la cantidad a cortar no exceda el stock disponible.
        """
        # Obtener el stock más reciente para el producto
        latest_stock = self.product.stocks.latest('date')
        
        if self.cutting_quantity > latest_stock.quantity:
            raise ValidationError(f"The cutting quantity ({self.cutting_quantity}) cannot exceed the available stock ({latest_stock.quantity}).")

    def save(self, *args, **kwargs):
        """
        Validación antes de guardar para asegurarse de que la cantidad es válida.
        """
        self.clean()  # Llama al método clean() para validar antes de guardar
        super().save(*args, **kwargs)

    def start_cutting(self, operator):
        """
        Método para iniciar el corte, actualiza el estado a 'in_process' y asigna el operario.
        """
        if self.status != 'pending':
            raise ValueError("The operation is not in 'pending' status.")
        
        self.status = 'in_process'
        self.operator = operator
        self.save()

    def complete_cutting(self):
        """
        Método para finalizar el corte, actualizar el stock y marcar la orden como 'completed'.
        """
        if self.status != 'in_process':
            raise ValueError("The operation must be in 'in_process' status to be completed.")

        # Actualiza el stock del producto (último stock registrado)
        latest_stock = self.product.stocks.latest('date')
        
        if latest_stock.quantity < self.cutting_quantity:
            raise ValueError("Not enough stock to complete the operation.")

        # Reducir el stock y guardar
        latest_stock.quantity -= self.cutting_quantity
        latest_stock.save()

        # Marca la orden como finalizada
        self.status = 'completed'
        self.completed_at = now()
        self.save()

    class Meta:
        permissions = [
            ("can_assign_order", "Can assign a cutting order"),
            ("can_process_order", "Can process a cutting order"),
        ]
