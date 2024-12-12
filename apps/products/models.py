import base64
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Product(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField(null=False, default=0, unique=True)
    type = models.ForeignKey('Type', on_delete=models.SET_NULL, related_name='products', null=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, related_name='products', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='products', null=True)
    status = models.BooleanField(default=True)

    def delete(self, *args, **kwargs):
        """Marca el producto como inactivo en lugar de eliminarlo."""
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def __str__(self):
        return self.name


class SubProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='subproducts')
    name = models.CharField(max_length=100, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    number_coil = models.PositiveIntegerField(null=True, blank=True)
    initial_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Ejemplo en metros
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Ejemplo en kilogramos
    coil_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Ejemplo en kilogramos
    technical_sheet_photo = models.ImageField(upload_to='technical_sheets/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Procesar `technical_sheet_photo` si está en formato Base64 en lugar de imagen
        if isinstance(self.technical_sheet_photo, str) and self.technical_sheet_photo.startswith('data:image'):
            format, imgstr = self.technical_sheet_photo.split(';base64,')
            ext = format.split('/')[-1]
            self.technical_sheet_photo = ContentFile(base64.b64decode(imgstr), name=f"{self.name}_tech_sheet.{ext}")

        super(SubProduct, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Marca el subproducto como inactivo en lugar de eliminarlo."""
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def __str__(self):
        return f'{self.product.name} - {self.name}'


class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='categories', null=True)
    status = models.BooleanField(default=True)
    
    def delete(self, *args, **kwargs):
        """Marca la categoría como inactiva en lugar de eliminarla."""
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='types', null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='types', null=True)
    status = models.BooleanField(default=True)
    
    def delete(self, *args, **kwargs):
        """Marca el tipo como inactivo en lugar de eliminarlo."""
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def __str__(self):
        return self.name
