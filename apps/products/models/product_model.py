from django.db import models

from apps.products.models.category_model import Category
from apps.products.models.type_model import Type
from apps.products.models.base_model import BaseModel  


class Product(BaseModel):
    """Modelo de Producto con relación a stock y subproductos."""
    
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.IntegerField(unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    status = models.BooleanField(default=True)  # Activo por defecto
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.name} ({self.code})'
