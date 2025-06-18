from django.db import models
from apps.products.models.product_model import Product

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_images",
        verbose_name="Producto"
    )
    key = models.CharField(
        max_length=255,
        default="temp-key",  # ✅ Default temporal
        verbose_name="Nombre del archivo en S3 (key)"
    )
    url = models.URLField(
        max_length=500,
        default="http://localhost/fake-url",  # ✅ Default temporal
        verbose_name="URL pública en S3"
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nombre del archivo"
    )
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Tipo MIME"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Productos"

    def __str__(self):
        return f"Imagen {self.id} de {self.product.name}"
