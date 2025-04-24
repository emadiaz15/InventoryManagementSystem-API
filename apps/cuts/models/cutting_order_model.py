from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

# Ajusta las rutas de importación según tu estructura
from apps.products.models.subproduct_model import Subproduct
from apps.products.models.base_model import BaseModel

# --- IMPORTA EL SERVICIO DE STOCK ---
from apps.stocks.services import dispatch_subproduct_stock_for_cut
# ------------------------------------


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
        """
        Alias al campo `created_by` de BaseModel, que representa quién creó/asignó la orden.
        """
        return self.created_by

    def clean(self):
        super().clean()
        # validación mínima: al menos un item con cantidad >0
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
        Completa la orden iterando sobre cada item y despachando stock vía servicio.
        """
        if self.workflow_status != 'in_process':
            raise ValidationError("Debe estar en 'En Proceso' para completarse.")
        if not user_completing or not user_completing.is_authenticated:
            raise ValidationError('Usuario inválido.')

        # despachar stock para cada item
        for item in self.items.select_for_update():
            dispatch_subproduct_stock_for_cut(
                subproduct=item.subproduct,
                cutting_quantity=item.cutting_quantity,
                order_pk=self.pk,
                user_performing_cut=user_completing,
                location=None
            )

        # marcar como completada
        self.workflow_status = 'completed'
        self.completed_at = timezone.now()
        self.save(
            user=user_completing,
            update_fields=['workflow_status','completed_at','modified_at','modified_by']
        )
        print(f"--- Orden {self.pk} completada ---")


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
