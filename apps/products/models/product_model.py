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
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nombre")
    code = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Código")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    brand = models.CharField(max_length=255, null=True, blank=True, verbose_name="Marca")
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ubicación")
    position = models.CharField(max_length=255, null=True, blank=True, verbose_name="Posición")
    # --- Relaciones ForeignKey ---
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT, # Cambiado a PROTECT (más seguro)
        related_name='products',
        null=False, blank=False, # Hecho obligatorio
        verbose_name="Categoría"
    )
    type = models.ForeignKey(
        Type,
        on_delete=models.PROTECT, # Cambiado a PROTECT
        related_name='products',
        null=False, blank=False, # Hecho obligatorio
        verbose_name="Tipo"
    )

    # --- NUEVO CAMPO PARA CONTROL DE STOCK ---
    has_individual_stock = models.BooleanField(
        default=True, # Por defecto, un producto nuevo maneja su stock individualmente
        verbose_name="Tiene Stock Individual",
        help_text="Si es True, el stock se busca en ProductStock. Si es False, se calcula desde SubproductStock."
    )
    # -----------------------------------------

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        name_display = self.name if self.name else "Producto sin nombre"
        code_display = self.code if self.code is not None else "Sin código"
        return f'{name_display} ({code_display})'
