from django.db import models
from apps.products.models.subproduct_model import Subproduct


class SubproductImage(models.Model):
    """
    Modelo de imágenes multimedia asociadas a un subproducto.
    """
    subproduct = models.ForeignKey(
        Subproduct,
        on_delete=models.CASCADE,
        related_name="subproduct_images",
        verbose_name="Subproducto"
    )
    drive_file_id = models.CharField(
        max_length=255,
        verbose_name="ID en Google Drive"
    )
    url = models.URLField(  # 🆕 NUEVO
        max_length=500,
        blank=True,
        null=True,
        verbose_name="URL de descarga directa"
    )
    name = models.CharField(  # 🆕 NUEVO
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nombre del archivo"
    )
    mimeType = models.CharField(  # 🆕 NUEVO
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
