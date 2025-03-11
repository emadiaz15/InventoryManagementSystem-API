from django.db import models
from django.utils import timezone
from django.db.models import Sum
from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product

class Subproduct(BaseModel):
    """Modelo de Subproducto con atributos específicos para cables."""

    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(max_length=500, null=True, blank=True)
    status = models.BooleanField(default=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    number_coil = models.PositiveIntegerField(null=True, blank=True)
    initial_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coil_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    technical_sheet_photo = models.ImageField(upload_to='technical_sheets/', null=True, blank=True)
    parent = models.ForeignKey(Product , on_delete=models.CASCADE, related_name='subproducts')
    quantity = models.PositiveIntegerField()     
    def __str__(self):
        return f'{self.parent.name} "SUBPRODUCTO"'
