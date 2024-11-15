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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cutting_orders', null=True)
    subproduct = models.ForeignKey(SubProduct, null=True, blank=True, on_delete=models.SET_NULL, related_name='cutting_orders')  # Subproducto opcional
    customer = models.CharField(max_length=255, help_text="Customer name for whom the cutting order is made")
    cutting_quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Quantity in meters to cut")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_by = models.ForeignKey(User, related_name='assigned_orders', on_delete=models.SET_NULL, null=True)
    operator = models.ForeignKey(User, related_name='cutting_orders', on_delete=models.SET_NULL, null=True, blank=True)
    items = models.ManyToManyField('Item')  # Relación con los items
    deleted_at = models.DateTimeField(null=True, blank=True)  # Campo para soft delete

    def __str__(self):
        return f'Cutting Order {self.pk} for {self.customer} - Status: {self.status}'

    def clean(self):
        """
        Validación personalizada para asegurar que la cantidad a cortar no exceda el stock disponible del subproducto.
        """
        # Validación de stock, si tiene subproducto o producto
        if self.subproduct:  # Si se seleccionó un subproducto
            try:
                latest_stock = self.subproduct.stocks.latest('date')
            except Stock.DoesNotExist:
                raise ValidationError(f"No se encontró stock para el subproducto {self.subproduct.name}.")
        else:  # Si no se seleccionó un subproducto, usamos el producto
            try:
                latest_stock = self.product.stocks.latest('date')
            except Stock.DoesNotExist:
                raise ValidationError(f"No se encontró stock para el producto {self.product.name}.")

        if self.cutting_quantity > latest_stock.quantity:
            raise ValidationError(
                f"La cantidad de corte ({self.cutting_quantity}) no puede exceder el stock disponible ({latest_stock.quantity})."
            )

    def save(self, *args, **kwargs):
        self.clean()  # Llamamos a clean para validar antes de guardar
        super().save(*args, **kwargs)

    def start_cutting(self, operator):
        """
        Cambia el estado de la orden a 'in_process' y asigna un operador.
        """
        if self.status != 'pending':
            raise ValueError("La operación no está en estado 'pending'.")

        self.status = 'in_process'
        self.operator = operator
        self.save()

    def complete_cutting(self):
        """
        Completa la operación de corte, actualiza el stock y cambia el estado de la orden.
        """
        if self.status != 'in_process':
            raise ValueError("La operación debe estar en estado 'in_process' para ser completada.")

        # Verificación de stock antes de realizar el corte
        if self.subproduct:
            latest_stock = self.subproduct.stocks.latest('date')
        else:
            latest_stock = self.product.stocks.latest('date')

        if latest_stock.quantity < self.cutting_quantity:
            raise ValueError("No hay suficiente stock para completar la operación.")

        latest_stock.quantity -= self.cutting_quantity
        latest_stock.save()

        # Completar la orden de corte
        self.status = 'completed'
        self.completed_at = now()
        self.save()

    def soft_delete(self):
        """
        Marca la orden como eliminada (soft delete), estableciendo la fecha de eliminación.
        """
        self.deleted_at = now()
        self.save(update_fields=['deleted_at'])

    class Meta:
        permissions = [
            ("can_assign_order", "Can assign a cutting order"),
            ("can_process_order", "Can process a cutting order"),
        ]
        ordering = ['-created_at']  # Ordena por fecha de creación descendente
        
        
class Item(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    subproduct = models.ForeignKey(SubProduct, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.subproduct.name if self.subproduct else 'No Subproduct'}"