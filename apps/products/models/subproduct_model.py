from django.db import models
from django.utils import timezone
from django.db.models import Sum
from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product

class Subproduct(BaseModel):
    """Modelo de Subproducto con atributos específicos para cables."""

    name = models.CharField(max_length=200, null=False, blank=False)  # Obligatorio
    description = models.CharField(max_length=500, null=True, blank=True)  # Opcional
    status = models.BooleanField(default=True)  # Opcional
    brand = models.CharField(max_length=100, null=True, blank=True)  # Opcional
    number_coil = models.PositiveIntegerField(null=True, blank=True)  # Opcional
    initial_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Opcional
    final_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Opcional
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Opcional
    coil_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Opcional
    technical_sheet_photo = models.ImageField(upload_to='technical_sheets/', null=True, blank=True)  # Opcional
    parent = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='subproducts', null=False, blank=False)    # Relación obligatoria
    quantity = models.PositiveIntegerField(null=False, blank=False, default=0)  # Obligatorio

