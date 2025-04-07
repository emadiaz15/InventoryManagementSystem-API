from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product

class Subproduct(BaseModel):
    """Modelo de Subproducto con atributos específicos, hereda de BaseModel."""

    # --- Campos Específicos del Subproducto ---
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(max_length=500, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    number_coil = models.PositiveIntegerField(null=True, blank=True, verbose_name="Número de Bobina")
    initial_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Longitud Inicial (m)")
    final_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Longitud Final (m)")
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Peso Total (kg)")
    coil_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Peso Bobina (kg)")
    technical_sheet_photo = models.ImageField(upload_to='technical_sheets/', null=True, blank=True, verbose_name="Foto Ficha Técnica")

    # --- Relación ForeignKey ---
    parent = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='subproducts',
        null=False, blank=False,
        verbose_name="Producto Padre"
    )

    class Meta:
        verbose_name = "Subproducto"
        verbose_name_plural = "Subproductos"

    def __str__(self):
        parent_name = getattr(self.parent, 'name', 'N/A')
        return f'{self.name} (Padre: {parent_name})'
