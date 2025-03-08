# apps/products/models/subproduct_model.py
from django.db import models
from django.utils import timezone

from django.contrib.auth import get_user_model

from apps.products.models.base_model import BaseModel

User = get_user_model()

class Subproduct(BaseModel):
    """Modelo para atributos especiales de 'cables'."""
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
    comments = models.ManyToManyField('comments.Comment', related_name='subproducts', blank=True)
    stocks = models.ManyToManyField('stocks.Stock', related_name='subproducts', blank=True)
    def delete(self, *args, **kwargs):
        """Soft delete con fecha."""
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def __str__(self):
        return f'{self.parent.name} "SUBPRODUCTO"'

    @property
    def parent(self):
        # Importamos el modelo Product aquí para evitar el ciclo de importación
        from apps.products.models.product_model import Product
        return Product.objects.get(id=self.parent_id)
