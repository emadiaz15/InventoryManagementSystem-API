from django.core.exceptions import ObjectDoesNotExist
from apps.products.models.subproduct_image_model import SubproductImage
from apps.products.models.subproduct_model import Subproduct
from django.conf import settings
import os

class SubproductFileRepository:
    """
    Repositorio para archivos de Subproduct adaptado para MinIO/S3.
    Permite listar, crear y eliminar registros de SubproductImage.
    """

    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_UPLOAD_EXTENSIONS", ".jpg,.jpeg,.png,.webp,.pdf").split(",")

    @staticmethod
    def get_all_by_subproduct(subproduct_id: int):
        return SubproductImage.objects.filter(subproduct_id=subproduct_id).order_by("created_at")

    @staticmethod
    def get_by_id(file_id: str):
        try:
            return SubproductImage.objects.get(key=file_id)
        except SubproductImage.DoesNotExist:
            return None

    @staticmethod
    def exists(subproduct_id: int, file_id: str) -> bool:
        exists = SubproductImage.objects.filter(
            subproduct_id=subproduct_id,
            key=file_id
        ).exists()
        if not exists:
            print(f"🛑 NO EXISTE SubproductFile: key={file_id}, subproduct_id={subproduct_id}")
        return exists

    @staticmethod
    def delete(file_id: str):
        try:
            img = SubproductImage.objects.get(key=file_id)
            img.delete()
            return img
        except SubproductImage.DoesNotExist:
            return None

    @staticmethod
    def create(
        subproduct_id: int,
        key: str,
        url: str = "",
        name: str = "",
        mime_type: str = ""
    ) -> SubproductImage:
        ext = os.path.splitext(name or key)[-1].lower()
        if ext not in SubproductFileRepository.ALLOWED_EXTENSIONS:
            raise ValueError(f"Extensión de archivo no permitida: {ext}. Permitidas: {SubproductFileRepository.ALLOWED_EXTENSIONS}")

        try:
            subp = Subproduct.objects.get(pk=subproduct_id, status=True)
        except Subproduct.DoesNotExist:
            raise ValueError(f"Subproducto con ID {subproduct_id} no existe o está inactivo.")

        return SubproductImage.objects.create(
            subproduct=subp,
            key=key,
            url=url,
            name=name,
            mimeType=mime_type
        )
