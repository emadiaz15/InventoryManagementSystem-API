from django.db import models
from apps.products.models.base_model import BaseModel
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type

class Product(BaseModel):
    """
    Modelo de Producto.
    Hereda campos de auditoría, estado activo/inactivo y ordenamiento de BaseModel.
    El stock se maneja en la app 'stock'. Incluye un flag para saber si tiene
    stock individual o derivado de subproductos.
    """

    # --- Campos Específicos del Producto ---
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Nombre"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Código"
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Descripción"
    )
    brand = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Marca"
    )
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Ubicación"
    )
    position = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Posición"
    )
    # --- Relaciones ForeignKey ---
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,  # Más seguro que CASCADE
        related_name='products',
        null=False,
        blank=False,
        verbose_name="Categoría"
    )
    type = models.ForeignKey(
        Type,
        on_delete=models.PROTECT,
        related_name='products',
        null=False,
        blank=False,
        verbose_name="Tipo"
    )

    # --- NUEVO CAMPO PARA CONTROL DE STOCK ---
    has_individual_stock = models.BooleanField(
        default=True,
        verbose_name="Tiene Stock Individual",
        help_text=(
            "Si es True, el stock se busca en ProductStock. "
            "Si es False, se calcula desde SubproductStock."
        )
    )
    # -----------------------------------------

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        # <— Aquí forzamos el orden descendente por fecha de creación
        ordering = ['-created_at']

    def __str__(self):
        name_display = self.name or "Producto sin nombre"
        code_display = self.code or "Sin código"
        return f'{name_display} ({code_display})'
