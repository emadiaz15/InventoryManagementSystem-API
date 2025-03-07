import base64
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile

from django.contrib.auth import get_user_model

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product

User = get_user_model()

class Subproduct(BaseModel):
    """Modelo OneToOne para atributos especiales de 'cables'."""
    parent = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='cable_subproduct')
    brand = models.CharField(max_length=100, null=True, blank=True)
    number_coil = models.PositiveIntegerField(null=True, blank=True)
    initial_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coil_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    technical_sheet_photo = models.ImageField(upload_to='technical_sheets/', null=True, blank=True)
    
    name = models.CharField(max_length=200, unique=True, default='No especificado')  # Valor por defecto

    def save(self, *args, **kwargs):
        """Manejo de imagen en base64 y reutilización de la lógica de BaseModel"""
        # Si la imagen técnica está en base64, la decodificamos
        if isinstance(self.technical_sheet_photo, str) and self.technical_sheet_photo.startswith('data:image'):
            format, imgstr = self.technical_sheet_photo.split(';base64,')
            ext = format.split('/')[-1]
            self.technical_sheet_photo = ContentFile(base64.b64decode(imgstr), name=f"{self.parent.name}_tech_sheet.{ext}")
        
        # Llamamos al método `save` de BaseModel, asegurando que el usuario esté pasando si se requiere
        super(Subproduct).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Soft delete con fecha."""
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def __str__(self):
        return f'{self.parent.name} - Cable Attributes'
