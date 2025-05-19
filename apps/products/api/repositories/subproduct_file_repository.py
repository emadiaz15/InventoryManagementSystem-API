from django.core.exceptions import ObjectDoesNotExist
from apps.products.models.subproduct_image_model import SubproductImage
from apps.products.models.subproduct_model import Subproduct

class SubproductFileRepository:
    """
    Repositorio para archivos de Subproduct.
    Permite listar, crear y eliminar registros de SubproductImage asociados.
    """

    @staticmethod
    def get_all_by_subproduct(subproduct_id: int):
        """
        Lista todas las imágenes asociadas a un subproducto.
        """
        return SubproductImage.objects.filter(subproduct_id=subproduct_id).order_by("created_at")

    @staticmethod
    def get_by_id(file_id: str):
        """
        Obtiene un registro SubproductImage por su ID (drive_file_id).
        """
        try:
            return SubproductImage.objects.get(drive_file_id=file_id)
        except SubproductImage.DoesNotExist:
            return None

    @staticmethod
    def exists(subproduct_id: int, file_id: str) -> bool:
        """
        Indica si existe un archivo con ese drive_file_id para el subproducto dado.
        """
        exists = SubproductImage.objects.filter(
            subproduct_id=subproduct_id,
            drive_file_id=file_id
        ).exists()
        if not exists:
            print(f"🛑 NO EXISTE SubproductFile: file_id={file_id}, subproduct_id={subproduct_id}")
        return exists

    @staticmethod
    def delete(file_id: str):
        """
        Elimina el registro SubproductImage con ese drive_file_id y retorna la instancia eliminada.
        """
        try:
            img = SubproductImage.objects.get(drive_file_id=file_id)
            img.delete()
            return img
        except SubproductImage.DoesNotExist:
            return None

    @staticmethod
    def create(subproduct_id: int, drive_file_id: str, url: str = "", name: str = "", mime_type: str = "") -> SubproductImage:
        """
        Crea un nuevo SubproductImage vinculado al subproducto indicado.
        """
        try:
            subp = Subproduct.objects.get(pk=subproduct_id, status=True)
        except Subproduct.DoesNotExist:
            raise ValueError(f"Subproducto con ID {subproduct_id} no existe o está inactivo.")

        return SubproductImage.objects.create(
            subproduct=subp,
            drive_file_id=drive_file_id,
            url=url,
            name=name,
            mimeType=mime_type
        )