from django.db import models
from apps.users.models import User
from apps.products.models import Product
from apps.stocks.models import Stock
from django.utils.timezone import now
from django.core.exceptions import ValidationError

class CuttingOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_process', 'In Process'),
        ('completed', 'Completed'),
    )

    # Cambiado SubProduct a Product
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.SET_NULL, related_name='cutting_orders'
    )
    customer = models.CharField(max_length=255, help_text="Customer for whom the cutting order is made")
    cutting_quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Quantity to cut in meters")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_by = models.ForeignKey(User, related_name='assigned_cutting_orders', on_delete=models.SET_NULL, null=True)
    assigned_to = models.ForeignKey(User, related_name='cutting_orders', on_delete=models.SET_NULL, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Cutting Order {self.pk} for {self.customer} - Status: {self.status}'

    def clean(self):
        if not self.product:
            raise ValidationError("A product must be selected for the cutting order.")
        
        try:
            stock = self.product.stocks.latest('created_at')
        except Stock.DoesNotExist:
            raise ValidationError(f"No stock available for product {self.product.name}.")

        if self.cutting_quantity > stock.quantity:
            raise ValidationError(f"Insufficient stock for product {self.product.name}. Available: {stock.quantity}")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def complete_cutting(self):
        if self.status != 'in_process':
            raise ValidationError("The order must be in 'in_process' status to complete.")

        try:
            stock = self.product.stocks.latest('created_at')
        except Stock.DoesNotExist:
            raise ValidationError(f"No stock available for product {self.product.name}.")

        if self.cutting_quantity > stock.quantity:
            raise ValidationError(f"Not enough stock to complete the order.")

        stock.quantity -= self.cutting_quantity
        stock.save()

        self.status = 'completed'
        self.completed_at = now()
        self.save()

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("can_assign_cutting_order", "Can assign cutting orders"),
            ("can_process_cutting_order", "Can process cutting orders"),
        ]
