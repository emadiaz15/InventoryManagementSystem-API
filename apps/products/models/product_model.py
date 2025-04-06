from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type


class Product(BaseModel): # Correcto: hereda de BaseModel
    """Modelo de Producto reutilizando lógica de BaseModel."""

    # --- Campos Específicos del Producto ---
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.IntegerField(unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # --- Relaciones ForeignKey ---
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT, # PROTECT suele ser más seguro que CASCADE para esto
        related_name='products', # related_name para acceder desde Category
        null=False # Asumimos que un producto SIEMPRE tiene categoría
    )
    type = models.ForeignKey(
        Type,
        on_delete=models.PROTECT, # PROTECT suele ser más seguro
        related_name='products', # related_name para acceder desde Type
        null=False # Asumimos que un producto SIEMPRE tiene tipo
    )

    def __str__(self):
        # Mostrar 'Sin nombre' o 'Sin código' si son None
        name_display = self.name if self.name else "Sin nombre"
        code_display = self.code if self.code is not None else "Sin código"
        return f'{name_display} ({code_display})'
