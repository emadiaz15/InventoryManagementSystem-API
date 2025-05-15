from django.db import models
from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product

class Subproduct(BaseModel):
    """Modelo de Subproducto con atributos específicos, hereda de BaseModel."""

    # --- Campos Específicos del Subproducto ---
    brand = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Marca"
    )
    number_coil = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Número de Bobina"
    )
    initial_enumeration = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Enumeración Inicial"
    )
    final_enumeration = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Enumeración Final"
    )
    gross_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso Bruto (kg)"
    )
    net_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso Neto (kg)"
    )
    initial_stock_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad de Stock Inicial"
    )
    location = models.CharField(
        max_length=100,
        choices=[
            ("Deposito Principal", "Depósito Principal"),
            ("Deposito Secundario", "Depósito Secundario"),
        ],
        default="Deposito Principal",
        verbose_name="Ubicación de Stock Inicial"
    )
    technical_sheet_photo = models.ImageField(
        upload_to='technical_sheets/',
        null=True,
        blank=True,
        verbose_name="Foto Ficha Técnica"
    )
    form_type = models.CharField(
        max_length=50,
        choices=[
            ("Bobina", "Bobina"),
            ("Rollo", "Rollo"),
        ],
        default="Bobina",
        verbose_name="Tipo de Forma"
    )
    observations = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observaciones"
    )

    # --- Relación ForeignKey ---
    parent = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='subproducts',
        null=False,
        blank=False,
        verbose_name="Producto Padre"
    )

    class Meta:
        verbose_name = "Subproducto"
        verbose_name_plural = "Subproductos"
        # Orden descendente por fecha de creación → los más nuevos primero
        ordering = ['-created_at']

    def __str__(self):
        parent_name = getattr(self.parent, 'name', 'N/A')
        brand_display = self.brand or "Sin marca"
        return f'{brand_display} (Padre: {parent_name})'
