import base64
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from django.db.models import Sum
from .base_model import BaseModel
from .category import Category
from .type_model import Type

class Product(BaseModel):
    """✅ Modelo de Producto reutilizando lógica de BaseModel con validación de código único"""
    code = models.IntegerField(unique=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)

    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subproducts'
    )

    def save(self, *args, **kwargs):
        """✅ Manejo de imagen en base64 y validación de código"""
        if isinstance(self.image, str) and self.image.startswith('data:image'):
            format, imgstr = self.image.split(';base64,')
            ext = format.split('/')[-1]
            self.image = ContentFile(base64.b64decode(imgstr), name=f"{self.name}_img.{ext}")

        self.validate_code(self.code)  # 🔥 Validamos que el código sea numérico
        super(Product, self).save(*args, **kwargs)

    @staticmethod
    def validate_code(value):
        """✅ Asegura que el código es un entero positivo"""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("El código del producto debe ser un número entero positivo.")
        return value

    @property
    def total_stock(self):
        """✅ Calcula el stock total sumando el propio + el de los subproductos"""
        return (
            self.stocks.filter(is_active=True).aggregate(total=Sum('quantity'))['total'] or 0
        ) + (
            self.subproducts.filter(status=True)
            .annotate(sub_stock=Sum('stocks__quantity'))
            .aggregate(total=Sum('sub_stock'))['total'] or 0
        )

class CableAttributes(models.Model):
    """✅ Modelo OneToOne para atributos especiales de 'cables'"""
    parent = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='cable_subproduct')
    brand = models.CharField(max_length=100, null=True, blank=True)
    number_coil = models.PositiveIntegerField(null=True, blank=True)
    initial_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coil_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    technical_sheet_photo = models.ImageField(upload_to='technical_sheets/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """✅ Manejo de imagen en base64"""
        if isinstance(self.technical_sheet_photo, str) and self.technical_sheet_photo.startswith('data:image'):
            format, imgstr = self.technical_sheet_photo.split(';base64,')
            ext = format.split('/')[-1]
            self.technical_sheet_photo = ContentFile(base64.b64decode(imgstr), name=f"{self.parent.name}_tech_sheet.{ext}")

        super(CableAttributes, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """✅ Soft delete con fecha"""
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def __str__(self):
        return f'{self.parent.name} - Cable Attributes'
