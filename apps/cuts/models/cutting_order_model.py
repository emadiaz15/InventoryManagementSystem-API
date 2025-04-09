from django.db import models, transaction # Importar transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# Ajusta las rutas de importación según tu estructura
from apps.products.models.subproduct_model import Subproduct
# Quitamos StockEvent/SubproductStock de aquí, los maneja el servicio
# from apps.stocks.models import SubproductStock, StockEvent
from apps.products.models.base_model import BaseModel

# --- IMPORTA EL SERVICIO DE STOCK ---
# Asegúrate de que la ruta sea correcta
from apps.stocks.services import dispatch_subproduct_stock_for_cut
# ------------------------------------

class CuttingOrder(BaseModel):
    """
    Modelo para órdenes de corte. Usa BaseModel y DELEGA la lógica
    de modificación de stock y creación de eventos a apps.stocks.services.
    """
    WORKFLOW_STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('in_process', 'En Proceso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    )
    workflow_status = models.CharField(
        max_length=20, choices=WORKFLOW_STATUS_CHOICES, default='pending', verbose_name="Estado del Flujo"
    )
    subproduct = models.ForeignKey(
        Subproduct, null=False, blank=False, on_delete=models.PROTECT,
        related_name='cutting_orders', verbose_name="Subproducto a Cortar"
    )
    customer = models.CharField(
        max_length=255, null=False, blank=False,
        help_text="Cliente para quien es la orden de corte", verbose_name="Cliente"
    )
    cutting_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False,
        help_text="Cantidad a cortar (ej. en metros)", verbose_name="Cantidad a Cortar"
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='assigned_cutting_orders',
        on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Asignado Por"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='cutting_orders_assigned',
        on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Asignado A"
    )
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Completado")

    # Hereda status(bool), created_at/by, modified_at/by, deleted_at/by de BaseModel

    class Meta:
        verbose_name = "Orden de Corte"
        verbose_name_plural = "Órdenes de Corte"
        permissions = [
            ("can_assign_cutting_order", "Can assign cutting orders"),
            ("can_process_cutting_order", "Can process cutting orders"),
        ]
        # ordering = ['-created_at'] # Heredado

    def __str__(self):
        return f'Orden {self.pk} - {self.subproduct} para {self.customer} ({self.get_workflow_status_display()})'

    def clean(self):
        """Validaciones a nivel de modelo."""
        super().clean()
        # Mantenemos la validación de stock aquí como una comprobación inicial,
        # pero la validación CRÍTICA (con select_for_update) está en el servicio.
        if self.subproduct_id and self.cutting_quantity is not None and self.cutting_quantity > 0:
            # Importar aquí para evitar dependencia circular si Stock hereda de BaseModel de products
            from apps.stocks.models import SubproductStock
            try:
                # Solo verifica si hay suficiente stock AHORA, sin bloquear.
                # La verificación final y bloqueo ocurre en el servicio al completar.
                stock = SubproductStock.objects.filter(subproduct=self.subproduct, status=True).latest('created_at')
                available_quantity = stock.quantity
            except SubproductStock.DoesNotExist:
                available_quantity = 0

            if self.cutting_quantity > available_quantity:
                raise ValidationError({
                    'cutting_quantity': f"Stock insuficiente para '{self.subproduct}'. "
                                      f"Disponible: {available_quantity}, Requerido: {self.cutting_quantity}"
                })

    # NO hay método save() aquí, se hereda el de BaseModel

    # --- MÉTODO complete_cutting (Refactorizado para usar Servicio) ---
    @transaction.atomic # Envuelve la completación de orden Y el despacho de stock
    def complete_cutting(self, user_completing):
        """
        Completa la orden de corte: LLAMA al servicio de stock para descontar
        y crear evento, luego actualiza el estado de la propia orden.
        """
        # 1. Validaciones propias de la orden de corte
        if self.workflow_status != 'in_process':
            raise ValidationError("La orden debe estar en estado 'En Proceso' para completarse.")
        if not self.subproduct_id:
             raise ValidationError("La orden no tiene un subproducto asociado.")
        if self.cutting_quantity is None or self.cutting_quantity <= 0:
             raise ValidationError("La cantidad a cortar no es válida.")
        if not user_completing or not user_completing.is_authenticated:
             raise ValidationError("Se requiere un usuario autenticado para completar la orden.")

        # 2. LLAMAR AL SERVICIO DE STOCK para descontar y registrar evento
        #    Pasamos los datos necesarios. El servicio maneja la transacción interna
        #    para actualizar SubproductStock y crear StockEvent.
        #    Asumimos que el stock se descuenta de la ubicación 'None' por defecto.
        #    Ajusta 'location' si es necesario.
        try:
            dispatch_subproduct_stock_for_cut(
                subproduct=self.subproduct,
                cutting_quantity=self.cutting_quantity,
                order_pk=self.pk, # Pasamos el ID de esta orden para la nota del evento
                user_performing_cut=user_completing,
                location=None # O especifica una ubicación si aplica
            )
        except (ValidationError, ValueError, ObjectDoesNotExist) as e:
             # Si el servicio de stock falla (ej. no hay stock suficiente al momento real),
             # la transacción hará rollback y la orden no se marcará como completada.
             # Relanzamos el error para que la vista/llamador lo maneje.
             raise ValidationError(f"No se pudo completar el corte por problema de stock: {e}")
        except Exception as e:
             # Otros errores inesperados
             raise Exception(f"Error inesperado al despachar stock para corte: {e}")


        # 3. Actualizar ESTA Orden de Corte
        self.workflow_status = 'completed'
        self.completed_at = timezone.now()
        # Guardamos la orden usando el save() de BaseModel, pasando el usuario
        # Se actualizarán workflow_status, completed_at, modified_at, modified_by
        self.save(
             user=user_completing,
             update_fields=['workflow_status', 'completed_at', 'modified_at', 'modified_by']
             )
        print(f"--- Modelo: Orden de Corte {self.pk} completada ---")
