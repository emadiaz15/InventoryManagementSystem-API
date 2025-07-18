from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.decorators.cache import cache_page
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema
import logging

from apps.products.models import Product
from apps.products.api.repositories.product_file_repository import ProductFileRepository
from apps.storages_client.services.products_files import (
    upload_product_file,
    delete_product_file,
    get_product_file_url
)
from apps.products.docs.product_image_doc import (
    product_image_upload_doc,
    product_image_list_doc,
    product_image_delete_doc,
    product_image_download_doc
)
from apps.products.utils.cache_helpers import (
    PRODUCT_LIST_CACHE_PREFIX,
    product_detail_cache_key
)

logger = logging.getLogger(__name__)
ALLOWED_CONTENT_TYPES = {
    "image/jpeg", "image/png", "image/webp",
    "application/pdf", "video/mp4", "video/webm"
}


@extend_schema(
    tags=product_image_upload_doc["tags"],
    summary=product_image_upload_doc["summary"],
    operation_id=product_image_upload_doc["operation_id"],
    description=product_image_upload_doc["description"],
    parameters=product_image_upload_doc["parameters"],
    request=product_image_upload_doc["requestBody"]["content"]["multipart/form-data"]["schema"],
    responses=product_image_upload_doc["responses"]
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def product_file_upload_view(request, product_id: str):
    get_object_or_404(Product, pk=product_id)
    files = request.FILES.getlist("file")

    if not files:
        return Response({"detail": "No se proporcionaron archivos."}, status=status.HTTP_400_BAD_REQUEST)

    invalid = [f.name for f in files if f.content_type not in ALLOWED_CONTENT_TYPES]
    if invalid:
        return Response(
            {"detail": f"Tipo de archivo no permitido en: {', '.join(invalid)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    results, errors = [], []
    for f in files:
        try:
            res = upload_product_file(file=f, product_id=int(product_id))
            ProductFileRepository.create(
                product_id=int(product_id),
                key=res["key"],
                url=res["url"],
                name=res["name"],
                mime_type=res["mimeType"]
            )
            results.append(res["key"])
        except Exception as e:
            logger.error(f"❌ Error subiendo archivo {f.name}: {e}")
            errors.append({f.name: str(e)})

    if results:
        # Invalida todas las páginas cacheadas de lista
        cache.delete_pattern(f"{PRODUCT_LIST_CACHE_PREFIX}*")
        # Invalida caché de detalle concreto
        cache.delete(product_detail_cache_key(product_id))

    if errors and not results:
        return Response(
            {"detail": "Ningún archivo pudo subirse.", "errors": errors},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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
    responses=product_image_list_doc["responses"]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_file_list_view(request, product_id: str):
    get_object_or_404(Product, pk=product_id)
    try:
        files = ProductFileRepository.get_all_by_product(int(product_id))
        return Response({"files": files}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"❌ Error listando archivos de producto {product_id}: {e}")
        return Response(
            {"detail": f"Error listando archivos: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=product_image_delete_doc["tags"],
    summary=product_image_delete_doc["summary"],
    operation_id=product_image_delete_doc["operation_id"],
    description=product_image_delete_doc["description"],
    parameters=product_image_delete_doc["parameters"],
    responses=product_image_delete_doc["responses"]
)
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def product_file_delete_view(request, product_id: str, file_id: str):
    get_object_or_404(Product, pk=product_id)
    if not ProductFileRepository.exists(int(product_id), file_id):
        return Response(
            {"detail": "El archivo no está asociado a este producto."},
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        delete_product_file(file_id)
        ProductFileRepository.delete(file_id)
        # Invalida cache lista y detalle
        cache.delete_pattern(f"{PRODUCT_LIST_CACHE_PREFIX}*")
        cache.delete(product_detail_cache_key(product_id))
        return Response({"detail": "Archivo eliminado correctamente."}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"❌ Error eliminando archivo {file_id} de producto {product_id}: {e}")
        return Response(
            {"detail": f"Error eliminando archivo: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=product_image_download_doc["tags"],
    summary=product_image_download_doc["summary"],
    operation_id=product_image_download_doc["operation_id"],
    description=product_image_download_doc["description"],
    parameters=product_image_download_doc["parameters"],
    responses=product_image_download_doc["responses"]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_file_download_view(request, product_id: str, file_id: str):
    get_object_or_404(Product, pk=product_id)
    if not ProductFileRepository.exists(int(product_id), file_id):
        return Response(
            {"detail": "El archivo no está asociado al producto."},
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        url = get_product_file_url(file_id)
        return HttpResponseRedirect(url)
    except Exception as e:
        logger.error(f"❌ Error generando URL presignada para {file_id}: {e}")
        return Response(
            {"detail": "Error generando acceso al archivo."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
