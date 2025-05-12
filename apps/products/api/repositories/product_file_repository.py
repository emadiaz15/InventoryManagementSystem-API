from django.core.exceptions import ObjectDoesNotExist
from apps.products.models.product_image_model import ProductImage
from apps.products.models.product_model import Product

class ProductNotFound(Exception):
    pass

class ProductFileRepository:

    @staticmethod
    def get_all_by_product(product_id: int):
        """Lista todas las imágenes asociadas a un producto."""
        return ProductImage.objects.filter(product_id=product_id)

    @staticmethod
    def get_by_id(file_id: str) -> ProductImage | None:
        """Obtiene una imagen por ID."""
        try:
            return ProductImage.objects.get(drive_file_id=file_id)
        except ProductImage.DoesNotExist:
            return None

    @staticmethod
    def exists(product_id: int, file_id: str) -> bool:
        query = ProductImage.objects.filter(product_id=product_id, drive_file_id=file_id)
        exists = query.exists()
        if not exists:
            print(f"🛑 NO EXISTE: file_id={file_id}, product_id={product_id}")
        return exists

    @staticmethod
    def delete(file_id: str) -> ProductImage | None:
        """Elimina la imagen si existe y retorna la instancia eliminada."""
        try:
            image = ProductImage.objects.get(drive_file_id=file_id)
            image.delete()
            return image
        except ProductImage.DoesNotExist:
            return None

    @staticmethod
    def create(product_id: int, drive_file_id: str) -> ProductImage:
        """Crea una nueva entrada de imagen vinculada a un producto."""
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise ProductNotFound(f"Producto con ID {product_id} no existe.")

        return ProductImage.objects.create(product=product, drive_file_id=drive_file_id)
