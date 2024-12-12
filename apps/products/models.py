import base64
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Category(models.Model):
    # Nombre de la categoría
    name = models.CharField(max_length=200)
    # Descripción opcional de la categoría
    description = models.TextField(null=True, blank=True)
    # Fecha de creación (asignada automáticamente al crear el registro)
    created_at = models.DateTimeField(auto_now_add=True)
    # Fecha de última modificación (asignada automáticamente al guardar)
    modified_at = models.DateTimeField(auto_now=True)
    # Fecha de borrado lógico (permite marcar el registro como inactivo sin borrarlo físicamente)
    deleted_at = models.DateTimeField(null=True, blank=True)
    # Usuario asociado a la categoría (opcional), útil para saber quién creó o maneja la categoría
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='categories', null=True)
    # Estado de la categoría: True=activa, False=inactiva
    status = models.BooleanField(default=True)
    
    def delete(self, *args, **kwargs):
        """
        Marca la categoría como inactiva en lugar de eliminarla físicamente.
        """
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])
        print("Category set to inactive successfully.")  # Mensaje en inglés

    def __str__(self):
        return self.name


class Type(models.Model):
    # Nombre del tipo
    name = models.CharField(max_length=200)
    # Descripción opcional del tipo
    description = models.TextField(null=True, blank=True)
    # Fecha de creación
    created_at = models.DateTimeField(auto_now_add=True)
    # Fecha de última modificación
    modified_at = models.DateTimeField(auto_now=True)
    # Fecha de borrado lógico
    deleted_at = models.DateTimeField(null=True, blank=True)
    # Usuario asociado al tipo (opcional)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='types', null=True)
    # Relación con una categoría (opcional), para organizar tipos por categoría
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='types', null=True)
    # Estado del tipo: True=activo, False=inactivo
    status = models.BooleanField(default=True)
    
    def delete(self, *args, **kwargs):
        """
        Marca el tipo como inactivo en lugar de eliminarlo físicamente.
        """
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])
        print("Type set to inactive successfully.")  # Mensaje en inglés

    def __str__(self):
        return self.name


class Product(models.Model):
    # Nombre del producto
    name = models.CharField(max_length=100)
    # Código numérico único del producto
    code = models.IntegerField(null=False, default=0, unique=True)
    # Relación auto-referencial para crear jerarquías (subproductos): 
    # Si es null, es un producto raíz; si no, es un subproducto de otro producto.
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='subproducts', null=True, blank=True)
    # Descripción opcional del producto
    description = models.TextField(null=True, blank=True)
    # Imagen opcional del producto (puede enviarse en Base64)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    # Relación opcional con una categoría
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    # Relación opcional con un tipo
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    # Fecha de creación
    created_at = models.DateTimeField(auto_now_add=True)
    # Fecha de última modificación
    modified_at = models.DateTimeField(auto_now=True)
    # Fecha de borrado lógico
    deleted_at = models.DateTimeField(null=True, blank=True)
    # Usuario asociado al producto (opcional)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    # Estado del producto: True=activo, False=inactivo
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        Procesa la imagen si es una cadena Base64 antes de guardar.
        """
        if isinstance(self.image, str) and self.image.startswith('data:image'):
            format, imgstr = self.image.split(';base64,')
            ext = format.split('/')[-1]
            self.image = ContentFile(base64.b64decode(imgstr), name=f"{self.name}_img.{ext}")
            print("Product image decoded from Base64.")  # Mensaje en inglés
        super(Product, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Marca el producto como inactivo en lugar de eliminarlo físicamente.
        """
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])
        print("Product set to inactive successfully.")  # Mensaje en inglés

    def __str__(self):
        return self.name


class CableAttributes(models.Model):
    # Este modelo contiene campos específicos para los productos de la categoría "Cables".
    # Solo se crea una instancia de CableAttributes para un producto si éste pertenece a la categoría Cables.
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='cable_attributes')
    # Campos específicos de cables:
    name = models.CharField(max_length=100, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    number_coil = models.PositiveIntegerField(null=True, blank=True)
    initial_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coil_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    technical_sheet_photo = models.ImageField(upload_to='technical_sheets/', null=True, blank=True)
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    # Estado: True=activo, False=inactivo
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        Procesa la foto técnica si es una cadena Base64 antes de guardar.
        """
        if isinstance(self.technical_sheet_photo, str) and self.technical_sheet_photo.startswith('data:image'):
            format, imgstr = self.technical_sheet_photo.split(';base64,')
            ext = format.split('/')[-1]
            self.technical_sheet_photo = ContentFile(base64.b64decode(imgstr), name=f"{self.name}_tech_sheet.{ext}")
            print("CableAttributes technical sheet photo decoded from Base64.")  # Mensaje en inglés
        super(CableAttributes, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Marca los atributos de cable como inactivos en lugar de eliminarlos físicamente.
        """
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])
        print("CableAttributes set to inactive successfully.")  # Mensaje en inglés

    def __str__(self):
        return f'{self.product.name} - Cable Attributes'
