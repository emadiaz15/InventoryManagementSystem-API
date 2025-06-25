from django.db import models
from apps.products.models.subproduct_model import Subproduct


class SubproductImage(models.Model):
    subproduct = models.ForeignKey(
        Subproduct,
        on_delete=models.CASCADE,
        related_name="subproduct_images",
        verbose_name="Subproducto"
    )
    key = models.CharField(
        max_length=255,
        default="temp-key",  # ⚠️ Default temporal solo para migrar
        verbose_name="Nombre del archivo en S3 (key)"
    )
    url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado en"
    )

    class Meta:
        verbose_name = "Imagen de Subproducto"
        verbose_name_plural = "Imágenes de Subproductos"

    def __str__(self):
        return f"Imagen {self.id} de Subproducto {self.subproduct.id}"
