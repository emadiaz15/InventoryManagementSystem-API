from django.core.cache import cache
from django.http import HttpResponseRedirect, Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema
import logging

from apps.products.models import Product, Subproduct
from apps.products.api.repositories.subproduct_file_repository import (
    SubproductFileRepository,
    ProductNotFound,
)
from apps.storages_client.services.subproducts_files import (
    upload_subproduct_file,
    delete_subproduct_file,
    get_subproduct_file_url,
)
from apps.products.docs.subproduct_image_doc import (
    subproduct_image_upload_doc,
    subproduct_image_list_doc,
    subproduct_image_download_doc,
    subproduct_image_delete_doc,
)
from apps.products.utils.cache_helpers_subproducts import (
    SUBPRODUCT_LIST_CACHE_PREFIX,
    subproduct_detail_cache_key,
)
from apps.products.utils.redis_utils import delete_keys_by_pattern

logger = logging.getLogger(__name__)


@extend_schema(
    tags=subproduct_image_upload_doc["tags"],
    summary=subproduct_image_upload_doc["summary"],
    operation_id=subproduct_image_upload_doc["operation_id"],
    description=subproduct_image_upload_doc["description"],
    parameters=subproduct_image_upload_doc["parameters"],
    request=subproduct_image_upload_doc["request"]["content"]["multipart/form-data"]["schema"],
    responses=subproduct_image_upload_doc["responses"],
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def subproduct_file_upload_view(request, product_id: str, subproduct_id: str):
    """
    Sube uno o varios archivos para un subproducto. La validación de extensiones
    se realiza en SubproductFileRepository.create(), lanzando ValidationError
    si la extensión no está permitida.
    """
    # 1) Verificar existencia de producto y subproducto
    try:
        product = Product.objects.get(pk=product_id, status=True)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Producto con ID {product_id} no existe.")
    try:
        subproduct = Subproduct.objects.get(
            pk=subproduct_id, parent_id=product.id, status=True
        )
    except Subproduct.DoesNotExist:
        raise Http404(
            f"Subproducto con ID {subproduct_id} no existe para el producto {product_id}."
        )

    files = request.FILES.getlist("file")
    if not files:
        return Response(
            {"detail": "No se proporcionaron archivos."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    results, errors = [], []
    for f in files:
        try:
            # 2) Subida a MinIO / S3
            res = upload_subproduct_file(
                file=f, product_id=product.id, subproduct_id=subproduct.id
            )

            # 3) Registro en BD + validación de extensión en repo
            SubproductFileRepository.create(
                subproduct_id=subproduct.id,
                key=res["key"],
                url=res["url"],
                name=res["name"],
                mime_type=res["mimeType"],
            )
            results.append(res["key"])
        except Exception as e:
            logger.exception(f"❌ Error subiendo archivo {f.name}: {e}")
            errors.append({f.name: str(e)})

    # 4) Invalidar cachés si algo subió
    if results:
        try:
            delete_keys_by_pattern(f"{SUBPRODUCT_LIST_CACHE_PREFIX}*")
            cache.delete(subproduct_detail_cache_key(product_id, subproduct_id))
        except NotImplementedError as nie:
            logger.warning(f"Redis no soporta eliminación por patrón, se omite: {nie}")

    # 5) Manejo de errores: 400 si sólo validación de extensión, 500 si no
    if errors and not results:
        all_validation = all(
            "Extensión de archivo no permitida" in list(err.values())[0] for err in errors
        )
        code = (
            status.HTTP_400_BAD_REQUEST
            if all_validation
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        detail = (
            "Archivos inválidos." if all_validation else "Ningún archivo pudo subirse."
        )
        return Response({"detail": detail, "errors": errors}, status=code)

    # 6) Respuesta parcial o total exitosa
    return Response(
        {"uploaded": results, "errors": errors or None},
        status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED,
    )


@extend_schema(
    tags=subproduct_image_list_doc["tags"],
    summary=subproduct_image_list_doc["summary"],
    operation_id=subproduct_image_list_doc["operation_id"],
    description=subproduct_image_list_doc["description"],
    parameters=subproduct_image_list_doc["parameters"],
    responses=subproduct_image_list_doc["responses"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subproduct_file_list_view(request, product_id: str, subproduct_id: str):
    # Verificar existencia
    try:
        product = Product.objects.get(pk=product_id, status=True)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Producto con ID {product_id} no existe.")
    try:
        subproduct = Subproduct.objects.get(
            pk=subproduct_id, parent_id=product.id, status=True
        )
    except Subproduct.DoesNotExist:
        raise Http404(
            f"Subproducto con ID {subproduct_id} no existe para el producto {product_id}."
        )

    try:
        files = SubproductFileRepository.get_all_by_subproduct(subproduct.id)
        return Response({"files": files}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(f"❌ Error listando archivos de subproducto {subproduct_id}: {e}")
        return Response(
            {"detail": f"Error listando archivos: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    tags=subproduct_image_download_doc["tags"],
    summary=subproduct_image_download_doc["summary"],
    operation_id=subproduct_image_download_doc["operation_id"],
    description=subproduct_image_download_doc["description"],
    parameters=subproduct_image_download_doc["parameters"],
    responses=subproduct_image_download_doc["responses"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subproduct_file_download_view(request, product_id: str, subproduct_id: str, file_id: str):
    # Verificar existencia
    try:
        product = Product.objects.get(pk=product_id, status=True)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Producto con ID {product_id} no existe.")
    try:
        subproduct = Subproduct.objects.get(
            pk=subproduct_id, parent_id=product.id, status=True
        )
    except Subproduct.DoesNotExist:
        raise Http404(
            f"Subproducto con ID {subproduct_id} no existe para el producto {product_id}."
        )

    if not SubproductFileRepository.exists(subproduct.id, file_id):
        raise Http404(
            f"Archivo {file_id} no está vinculado al subproducto {subproduct_id}."
        )

    try:
        url = get_subproduct_file_url(file_id)
        return HttpResponseRedirect(url)
    except Exception as e:
        logger.exception(
            f"❌ Error generando URL presignada para archivo {file_id} del subproducto {subproduct_id}: {e}"
        )
        return Response(
            {"detail": "Error generando acceso al archivo."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    tags=subproduct_image_delete_doc["tags"],
    summary=subproduct_image_delete_doc["summary"],
    operation_id=subproduct_image_delete_doc["operation_id"],
    description=subproduct_image_delete_doc["description"],
    parameters=subproduct_image_delete_doc["parameters"],
    responses=subproduct_image_delete_doc["responses"],
)
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def subproduct_file_delete_view(request, product_id: str, subproduct_id: str, file_id: str):
    # Verificar existencia
    try:
        product = Product.objects.get(pk=product_id, status=True)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Producto con ID {product_id} no existe.")
    try:
        subproduct = Subproduct.objects.get(
            pk=subproduct_id, parent_id=product.id, status=True
        )
    except Subproduct.DoesNotExist:
        raise Http404(
            f"Subproducto con ID {subproduct_id} no existe para el producto {product_id}."
        )

    if not SubproductFileRepository.exists(subproduct.id, file_id):
        return Response(
            {"detail": "El archivo no está vinculado a este subproducto."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        delete_subproduct_file(file_id)
        SubproductFileRepository.delete(file_id)
        try:
            delete_keys_by_pattern(f"{SUBPRODUCT_LIST_CACHE_PREFIX}*")
            cache.delete(subproduct_detail_cache_key(product_id, subproduct_id))
        except NotImplementedError as nie:
            logger.warning(f"Redis no soporta eliminación por patrón, se omite: {nie}")
        return Response(
            {"detail": "Archivo eliminado correctamente."},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.exception(f"❌ Error eliminando archivo {file_id} de subproducto {subproduct_id}: {e}")
        return Response(
            {"detail": f"Error eliminando archivo: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
