# apps/products/api/views/product_files_view.py

import logging
from django.http import HttpResponseRedirect, Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.products.models import Product
from apps.products.api.repositories.product_file_repository import (
    ProductFileRepository,
    ProductNotFound,
)
from apps.storages_client.services.products_files import (
    upload_product_file,
    delete_product_file,
    get_product_file_url,
)
from apps.products.docs.product_image_doc import (
    product_image_upload_doc,
    product_image_list_doc,
    product_image_download_doc,
    product_image_delete_doc,
)
from apps.products.utils.cache_helpers_products import (
    PRODUCT_LIST_CACHE_PREFIX,
    PRODUCT_DETAIL_CACHE_PREFIX,
)
from apps.products.utils.redis_utils import delete_keys_by_pattern

logger = logging.getLogger(__name__)


@extend_schema(
    tags=product_image_upload_doc["tags"],
    summary=product_image_upload_doc["summary"],
    operation_id=product_image_upload_doc["operation_id"],
    description=product_image_upload_doc["description"],
    parameters=product_image_upload_doc["parameters"],
    request=product_image_upload_doc["requestBody"]["content"]["multipart/form-data"]["schema"],
    responses=product_image_upload_doc["responses"],
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def product_file_upload_view(request, product_id: str):
    """
    Sube archivos para un producto; invalida caché de lista y detalle.
    """
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Producto con ID {product_id} no existe.")

    files = request.FILES.getlist("file")
    if not files:
        return Response({"detail": "No se proporcionaron archivos."}, status=status.HTTP_400_BAD_REQUEST)

    results, errors = [], []
    for f in files:
        try:
            res = upload_product_file(file=f, product_id=str(product.id))
            ProductFileRepository.create(
                product_id=product.id,
                key=res["key"],
                url=res["url"],
                name=res["name"],
                mime_type=res["mimeType"],
            )
            results.append(res["key"])
        except Exception as e:
            logger.exception(f"❌ Error subiendo archivo {f.name}: {e}")
            errors.append({f.name: str(e)})

    if results:
        # Invalidar caché de lista y detalle
        deleted_list   = delete_keys_by_pattern(PRODUCT_LIST_CACHE_PREFIX)
        deleted_detail = delete_keys_by_pattern(PRODUCT_DETAIL_CACHE_PREFIX)
        logger.debug(
            "[Cache] product_list invalidada (%d) y product_detail invalidada (%d) tras UPLOAD",
            deleted_list, deleted_detail
        )

    if errors and not results:
        only_ext_errors = all("Extensión de archivo no permitida" in list(err.values())[0] for err in errors)
        code = status.HTTP_400_BAD_REQUEST if only_ext_errors else status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = "Archivos inválidos." if only_ext_errors else "Ningún archivo pudo subirse."
        return Response({"detail": detail, "errors": errors}, status=code)

    return Response(
        {"uploaded": results, "errors": errors or None},
        status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED
    )


@extend_schema(
    tags=product_image_list_doc["tags"],
    summary=product_image_list_doc["summary"],
    operation_id=product_image_list_doc["operation_id"],
    description=product_image_list_doc["description"],
    parameters=product_image_list_doc["parameters"],
    responses=product_image_list_doc["responses"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_file_list_view(request, product_id: str):
    try:
        Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Producto con ID {product_id} no existe.")
    try:
        files = ProductFileRepository.get_all_by_product(product_id)
        return Response({"files": files}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(f"❌ Error listando archivos de producto {product_id}: {e}")
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=product_image_download_doc["tags"],
    summary=product_image_download_doc["summary"],
    operation_id=product_image_download_doc["operation_id"],
    description=product_image_download_doc["description"],
    parameters=product_image_download_doc["parameters"],
    responses=product_image_download_doc["responses"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_file_download_view(request, product_id: str, file_id: str):
    try:
        Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Producto con ID {product_id} no existe.")
    if not ProductFileRepository.exists(product_id, file_id):
        raise Http404("Archivo no vinculado al producto.")
    try:
        url = get_product_file_url(file_id)
        return HttpResponseRedirect(url)
    except Exception as e:
        logger.exception(f"❌ Error generando URL para {file_id}: {e}")
        return Response({"detail": "Error generando acceso al archivo."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=product_image_delete_doc["tags"],
    summary=product_image_delete_doc["summary"],
    operation_id=product_image_delete_doc["operation_id"],
    description=product_image_delete_doc["description"],
    parameters=product_image_delete_doc["parameters"],
    responses=product_image_delete_doc["responses"],
)
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def product_file_delete_view(request, product_id: str, file_id: str):
    try:
        Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Producto con ID {product_id} no existe.")
    if not ProductFileRepository.exists(product_id, file_id):
        return Response({"detail": "Archivo no vinculado al producto."}, status=status.HTTP_404_NOT_FOUND)
    try:
        delete_product_file(file_id)
        ProductFileRepository.delete(file_id)
        # Invalidar caché de lista y detalle
        deleted_list   = delete_keys_by_pattern(PRODUCT_LIST_CACHE_PREFIX)
        deleted_detail = delete_keys_by_pattern(PRODUCT_DETAIL_CACHE_PREFIX)
        logger.debug(
            "[Cache] product_list invalidada (%d) y product_detail invalidada (%d) tras DELETE",
            deleted_list, deleted_detail
        )
        return Response({"detail": "Archivo eliminado correctamente."}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(f"❌ Error eliminando archivo {file_id}: {e}")
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
