from django.db import models
from apps.products.models.product_model import Product

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_images",
        verbose_name="Producto"
    )
    drive_file_id = models.CharField(
        max_length=255,
        verbose_name="ID en Google Drive"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Productos"

    def __str__(self):
        return f"Imagen {self.id} de {self.product.name}"
