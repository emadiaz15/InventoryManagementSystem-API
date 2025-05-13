from django.db import models
from django.conf import settings
from apps.products.models.base_model import BaseModel
from apps.products.models.subproduct_model import Subproduct

class SubproductStock(BaseModel):
    """Stock para un Subproducto específico."""

    subproduct = models.ForeignKey( # Un subproducto puede estar en varias ubicaciones -> ForeignKey
        Subproduct,
        on_delete=models.CASCADE, # Si se borra el subproducto, se borra su stock
        related_name='stock_records', 
        verbose_name="Subproducto"
    )
    quantity = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="Cantidad Actual"
    )

    class Meta:
        verbose_name = "Stock de Subproducto"
        verbose_name_plural = "Stocks de Subproductos"
        # Asegura que no haya dos registros para el mismo subproducto en la misma ubicación
        unique_together = ['subproduct']

    def __str__(self):
        subproduct_name = getattr(self.subproduct, 'name', f'ID:{self.subproduct_id}')
        return f"Stock de {subproduct_name}: {self.quantity}"
