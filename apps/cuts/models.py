# Este archivo define el modelo CuttingOrder, que representa órdenes de corte para productos. 
# Incluye métodos para iniciar y completar cortes, validando que el stock esté disponible.

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
    deleted_at = models.DateTimeField(null=True, blank=True)  # Campo para soft delete

    # Managers
    objects = models.Manager()  # Manager por defecto

    def __str__(self):
        """
        Representación en cadena de la instancia de CuttingOrder.
        """
        return f'Cutting Order {self.pk} for {self.customer} - Status: {self.status}'

    def clean(self):
        """
        Validación personalizada para asegurar que la cantidad a cortar no exceda el stock disponible.
        """
        # Obtiene el stock más reciente del producto
        latest_stock = self.product.stocks.latest('date')
        
        if self.cutting_quantity > latest_stock.quantity:
            raise ValidationError(f"La cantidad de corte ({self.cutting_quantity}) no puede exceder el stock disponible ({latest_stock.quantity}).")

    def save(self, *args, **kwargs):
        """
        Guarda la instancia después de validar que la cantidad es válida.
        """
        # Valida la cantidad de corte con el método `clean`
        self.clean()
        super().save(*args, **kwargs)

    def start_cutting(self, operator):
        """
        Inicia el corte, actualiza el estado a 'in_process' y asigna el operario.
        """
        if self.status != 'pending':
            raise ValueError("La operación no está en estado 'pending'.")

        self.status = 'in_process'
        self.operator = operator
        self.save()

    def complete_cutting(self):
        """
        Finaliza el corte, actualiza el stock y marca la orden como 'completed'.
        """
        if self.status != 'in_process':
            raise ValueError("La operación debe estar en estado 'in_process' para ser completada.")

        # Obtiene el stock más reciente del producto
        latest_stock = self.product.stocks.latest('date')
        
        # Verifica que haya suficiente stock para completar el corte
        if latest_stock.quantity < self.cutting_quantity:
            raise ValueError("No hay suficiente stock para completar la operación.")

        # Reduce el stock y guarda
        latest_stock.quantity -= self.cutting_quantity
        latest_stock.save()

        # Marca la orden como completada y registra la fecha de finalización
        self.status = 'completed'
        self.completed_at = now()
        self.save()

    def delete(self, *args, **kwargs):
        """
        Soft delete: establece `deleted_at` en la fecha y hora actuales en lugar de eliminar el registro.
        """
        self.deleted_at = now()
        self.save(update_fields=['deleted_at'])

    class Meta:
        permissions = [
            ("can_assign_order", "Can assign a cutting order"),
            ("can_process_order", "Can process a cutting order"),
        ]
        ordering = ['-created_at']  # Ordena por fecha de creación descendente
