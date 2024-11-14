from django.db import models
from apps.users.models import User
from apps.products.models import Product, SubProduct  # Importar los modelos de 'products'
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from apps.stocks.models import Stock

class CuttingOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_process', 'In Process'),
        ('completed', 'Completed'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cutting_orders',null=True)
    subproduct = models.ForeignKey(SubProduct, null=True, blank=True, on_delete=models.SET_NULL, related_name='cutting_orders')  # Subproducto opcional
    customer = models.CharField(max_length=255, help_text="Customer name for whom the cutting order is made")
    cutting_quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Quantity in meters to cut")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_cutting_orders')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cutting_operations')
    completed_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Campo para soft delete

    def __str__(self):
        return f'Cutting Order {self.pk} for {self.customer} - Status: {self.status}'

    def clean(self):
        """
        Validación personalizada para asegurar que la cantidad a cortar no exceda el stock disponible del subproducto.
        """
        if self.subproduct:  # Si se seleccionó un subproducto
            latest_stock = self.subproduct.stocks.latest('date')
        else:  # Si no se seleccionó un subproducto, usamos el producto
            latest_stock = self.product.stocks.latest('date')

        if self.cutting_quantity > latest_stock.quantity:
            raise ValidationError(
                f"La cantidad de corte ({self.cutting_quantity}) no puede exceder el stock disponible ({latest_stock.quantity})."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def start_cutting(self, operator):
        if self.status != 'pending':
            raise ValueError("La operación no está en estado 'pending'.")

        self.status = 'in_process'
        self.operator = operator
        self.save()

    def complete_cutting(self):
        if self.status != 'in_process':
            raise ValueError("La operación debe estar en estado 'in_process' para ser completada.")

        if self.subproduct:
            latest_stock = self.subproduct.stocks.latest('date')
        else:
            latest_stock = self.product.stocks.latest('date')
        
        if latest_stock.quantity < self.cutting_quantity:
            raise ValueError("No hay suficiente stock para completar la operación.")

        latest_stock.quantity -= self.cutting_quantity
        latest_stock.save()

        self.status = 'completed'
        self.completed_at = now()
        self.save()

    def delete(self, *args, **kwargs):
        self.deleted_at = now()
        self.save(update_fields=['deleted_at'])

    class Meta:
        permissions = [
            ("can_assign_order", "Can assign a cutting order"),
            ("can_process_order", "Can process a cutting order"),
        ]
        ordering = ['-created_at']  # Ordena por fecha de creación descendente
        
    def clean(self):
    # Intenta obtener el stock más reciente para el subproducto
        try:
            latest_stock = self.subproduct.stocks.latest('date')
        except Stock.DoesNotExist:
            # Si no existe ningún stock para este subproducto, puedes decidir qué hacer
            # Podrías lanzar una excepción personalizada o simplemente asignar un valor predeterminado
            latest_stock = None  # O maneja el caso según tu lógica

        if latest_stock is None:
            # Aquí puedes decidir cómo manejar el caso cuando no hay stock disponible
            # Por ejemplo, lanzar una excepción con un mensaje descriptivo
            raise ValidationError("No hay registros de stock para este subproducto.")