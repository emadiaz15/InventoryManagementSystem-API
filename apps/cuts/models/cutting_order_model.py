from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

from apps.products.models.subproduct_model import Subproduct
from apps.products.models.product_model import Product
from apps.products.models.base_model import BaseModel


class CuttingOrder(BaseModel):
    WORKFLOW_STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('in_process', 'En Proceso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    )

    workflow_status = models.CharField(
        max_length=20,
        choices=WORKFLOW_STATUS_CHOICES,
        default='pending',
        verbose_name='Estado del Flujo'
    )
    order_number = models.PositiveIntegerField(
        verbose_name='Número de Pedido',
        help_text='Número de pedido manual, entero único',
        unique=True,
        default=0
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='cutting_orders',
        verbose_name='Producto'
    )
    customer = models.CharField(
        max_length=255,
        help_text='Cliente para quien es la orden de corte',
        verbose_name='Cliente'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='cutting_orders_assigned',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Asignado A'
    )
    completed_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Fecha de Completado'
    )
    operator_can_edit_items = models.BooleanField(
        default=False,
        verbose_name='Operario puede editar items'
    )

    class Meta:
        verbose_name = 'Orden de Corte'
        verbose_name_plural = 'Órdenes de Corte'
        permissions = [
            ('can_assign_cutting_order', 'Can assign cutting orders'),
            ('can_process_cutting_order', 'Can process cutting orders'),
        ]

    def __str__(self):
        return f'Orden {self.pk} para {self.customer} ({self.get_workflow_status_display()})'

    @property
    def assigned_by(self):
        return self.created_by

    def clean(self):
        super().clean()
        if not self.items.exists():
            raise ValidationError('Debe incluir al menos un item de corte.')
        for item in self.items.all():
            if item.cutting_quantity <= 0:
                raise ValidationError({
                    'items': f"Cantidad inválida para {item.subproduct}."
                })

    @transaction.atomic
    def complete_cutting(self, user_completing):
        """
        Llama a un servicio externo que maneja la lógica de stock y estado.
        Se importa dentro del método para evitar ciclos de importación.
        """
        from apps.cuts.services.cuts_services import complete_cutting_logic
        return complete_cutting_logic(self, user_completing)


class CuttingOrderItem(models.Model):
    order = models.ForeignKey(
        CuttingOrder,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name="Orden de Corte"
    )
    subproduct = models.ForeignKey(
        Subproduct,
        on_delete=models.PROTECT,
        verbose_name="Subproducto"
    )
    cutting_quantity = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Cantidad a cortar de este subproducto"
    )

    class Meta:
        verbose_name = "Item de Orden de Corte"
        verbose_name_plural = "Items de Orden de Corte"

    def __str__(self):
        return f"{self.subproduct} → {self.cutting_quantity}"
