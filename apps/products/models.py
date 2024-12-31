import base64
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='categories', null=True)
    status = models.BooleanField(default=True)

    def delete(self, *args, **kwargs):
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
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField(null=False, default=0, unique=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if isinstance(self.image, str) and self.image.startswith('data:image'):
            format, imgstr = self.image.split(';base64,')
            ext = format.split('/')[-1]
            self.image = ContentFile(base64.b64decode(imgstr), name=f"{self.name}_img.{ext}")
        super(Product, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def __str__(self):
        return self.name


class CableAttributes(models.Model):
    # Subproducto del Producto principal
    parent = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='cable_subproduct',
        help_text="Producto principal al que pertenece este subproducto (Cable Attributes)."
    )
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
        if isinstance(self.technical_sheet_photo, str) and self.technical_sheet_photo.startswith('data:image'):
            format, imgstr = self.technical_sheet_photo.split(';base64,')
            ext = format.split('/')[-1]
            self.technical_sheet_photo = ContentFile(base64.b64decode(imgstr), name=f"{self.parent.name}_tech_sheet.{ext}")
        super(CableAttributes, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def __str__(self):
        return f'{self.parent.name} - Cable Attributes'
