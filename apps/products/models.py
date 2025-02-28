import base64
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='categories', null=True
    )
    status = models.BooleanField(default=True)

    def delete(self, *args, **kwargs):
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='types', null=True
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='types', null=True
    )
    status = models.BooleanField(default=True)

    def delete(self, *args, **kwargs):
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Modelo principal para productos.
    - Enfoque mixto: un producto puede tener subproductos,
      pero también tener stock propio.
    """
    name = models.CharField(max_length=100)
    code = models.IntegerField(null=False, default=0, unique=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    # Categoría y Tipo, como antes
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='products', null=True, blank=True
    )
    type = models.ForeignKey(
        Type, on_delete=models.SET_NULL,
        related_name='products', null=True, blank=True
    )

    # Campo para manejo de subproductos (jerarquía)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='subproducts',
        help_text="Si no es nulo, indica que este producto es un subproducto de otro."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='products', null=True, blank=True
    )
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Manejo de imagen en base64 (si aplica)
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
        # Si es subproducto, podrías mostrarlo distinto
        if self.parent:
            return f"[Subproduct] {self.name} (Parent: {self.parent.name})"
        return self.name

    @property
    def total_stock(self):
        """
        Ejemplo de propiedad para obtener el stock total (Enfoque mixto):
         - Si el producto tiene subproductos, se suma la propia cantidad + la de cada subproducto.
         - Si no tiene subproductos, simplemente retorna la propia cantidad.

        NOTA: Ajustar a tu app 'stocks' (ej: product.stocks).
        """
        # 1) Stock propio
        own_stock = 0
        # Supongamos que tu Stock model define una relación
        # product = ForeignKey(Product, ...) con related_name='stocks'
        # Y tomamos, por ejemplo, el último registro activo
        last_own_stock = self.stocks.filter(is_active=True).order_by('-created_at').first()
        if last_own_stock:
            own_stock = last_own_stock.quantity

        # 2) Sumar stock de subproductos
        total_subproducts_stock = 0
        for sub in self.subproducts.filter(status=True):
            sub_stock_obj = sub.stocks.filter(is_active=True).order_by('-created_at').first()
            sub_stock = sub_stock_obj.quantity if sub_stock_obj else 0
            total_subproducts_stock += sub_stock

        # Retornamos la suma (producto padre + subproductos)
        return own_stock + total_subproducts_stock


class CableAttributes(models.Model):
    """
    Modelo OneToOne para atributos especiales de 'cables'.
    """
    parent = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='cable_subproduct',
        help_text="Producto principal (cable) al que pertenecen estos atributos."
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
        # Manejo de foto en base64 (si aplica)
        if (
            isinstance(self.technical_sheet_photo, str)
            and self.technical_sheet_photo.startswith('data:image')
        ):
            format, imgstr = self.technical_sheet_photo.split(';base64,')
            ext = format.split('/')[-1]
            self.technical_sheet_photo = ContentFile(
                base64.b64decode(imgstr),
                name=f"{self.parent.name}_tech_sheet.{ext}"
            )
        super(CableAttributes, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.status = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['status', 'deleted_at'])

    def __str__(self):
        return f'{self.parent.name} - Cable Attributes'
