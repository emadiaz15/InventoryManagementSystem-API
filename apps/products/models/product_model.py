import base64
from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from .base_model import BaseModel
from .category_model import Category
from .type_model import Type

User = get_user_model()

class Product(BaseModel):
    """Modelo de Producto reutilizando lógica de BaseModel con validación de código único."""
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.IntegerField(unique=True, null=True, blank=True)  # Hacer el campo opcional
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subproducts'
    )

    def save(self, *args, **kwargs):
        """Manejo de imagen en base64 y validación de código"""
        # Si la imagen es proporcionada en formato base64
        if isinstance(self.image, str) and self.image.startswith('data:image'):
            format, imgstr = self.image.split(';base64,')
            ext = format.split('/')[-1]
            self.image = ContentFile(base64.b64decode(imgstr), name=f"{self.name}_img.{ext}")

        # Validación del código del producto (solo si el código es proporcionado)
        if self.code is not None:
            self.validate_code(self.code)

        super(Product, self).save(*args, **kwargs)

    @staticmethod
    def validate_code(code):
        """Validación del código del producto"""
        if not isinstance(code, int) or code <= 0:
            raise ValueError("El código del producto debe ser un número entero positivo.")

    @property
    def total_stock(self):
        """Calcula el stock total sumando el propio + el de los subproductos"""
        # Asegura que el stock total de productos y subproductos sea calculado de manera eficiente
        return (
            self.stocks.filter(is_active=True).aggregate(total=Sum('quantity'))['total'] or 0
        ) + (
            self.subproducts.filter(status=True)
            .annotate(sub_stock=Sum('stocks__quantity'))
            .aggregate(total=Sum('sub_stock'))['total'] or 0
        )
