import os
import logging
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from apps.products.models.product_image_model import ProductImage
from apps.products.models.product_model import Product
from apps.storages_client.services.products_files import get_product_file_url

logger = logging.getLogger(__name__)

class ProductNotFound(Exception):
    pass

class ProductFileRepository:
    """
    Repositorio para archivos asociados a productos.
    """

    @staticmethod
    def _validate_file_extension(filename: str):
        allowed = os.getenv("ALLOWED_UPLOAD_EXTENSIONS", "").split(",")
        _, ext = os.path.splitext(filename.lower())
        if ext not in allowed:
            raise ValidationError(f"Extensión de archivo no permitida: {ext}. Permitidas: {allowed}")

    @staticmethod
    def get_all_by_product(product_id: int):
        """Lista todas las imágenes asociadas a un producto con URL generada."""
        return [
            {
                "key": f.key,
                "name": f.name,
                "mimeType": f.mime_type,
                "url": get_product_file_url(f.key)
            }
            for f in ProductImage.objects.filter(product_id=product_id)
        ]

    @staticmethod
    def get_by_id(file_id: str) -> ProductImage | None:
        try:
            return ProductImage.objects.get(key=file_id)
        except ProductImage.DoesNotExist:
            return None

    @staticmethod
    def exists(product_id: int, file_id: str) -> bool:
        return ProductImage.objects.filter(product_id=product_id, key=file_id).exists()

    @staticmethod
    def delete(file_id: str) -> ProductImage | None:
        try:
            image = ProductImage.objects.get(key=file_id)
            image.delete()
            return image
        except ProductImage.DoesNotExist:
            return None

    @staticmethod
    def create(product_id: int, key: str, url: str = None, name: str = None, mime_type: str = None) -> ProductImage:
        ProductFileRepository._validate_file_extension(name or key)
        product = Product.objects.get(pk=product_id)
        return ProductImage.objects.create(
            product=product,
            key=key,
            url=url,
            name=name,
            mime_type=mime_type
        )