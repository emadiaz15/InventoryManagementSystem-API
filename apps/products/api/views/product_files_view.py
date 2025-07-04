from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
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

logger = logging.getLogger(__name__)
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf", "video/mp4", "video/webm"}

CACHE_KEY_PRODUCT_LIST = "views.decorators.cache.cache_page./api/v1/inventory/products/"

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

    invalid_files = [f.name for f in files if f.content_type not in ALLOWED_CONTENT_TYPES]
    if invalid_files:
        return Response(
            {"detail": f"Tipo de archivo no permitido en: {', '.join(invalid_files)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    results, errors = [], []
    for file in files:
        try:
            result = upload_product_file(file=file, product_id=int(product_id))
            ProductFileRepository.create(
                product_id=int(product_id),
                key=result["key"],
                url=result["url"],
                name=result["name"],
                mime_type=result["mimeType"]
            )
            results.append(result["key"])
        except Exception as e:
            logger.error(f"❌ Error subiendo archivo {file.name}: {e}")
            errors.append({file.name: str(e)})

    if results:
        cache.delete(CACHE_KEY_PRODUCT_LIST)

    if errors and not results:
        return Response(
            {"detail": "Ningún archivo pudo subirse.", "errors": errors},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {"uploaded": results, "errors": errors if errors else None},
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
        return Response({"detail": f"Error listando archivos: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        return Response({"detail": "El archivo no está asociado a este producto."}, status=status.HTTP_404_NOT_FOUND)

    try:
        delete_product_file(file_id)
        ProductFileRepository.delete(file_id)
        cache.delete(CACHE_KEY_PRODUCT_LIST)
        return Response({"detail": "Archivo eliminado correctamente."}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"❌ Error eliminando archivo {file_id} de producto {product_id}: {e}")
        return Response({"detail": f"Error eliminando archivo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        return Response({"detail": "El archivo no está asociado al producto."}, status=status.HTTP_404_NOT_FOUND)

    try:
        url = get_product_file_url(file_id)
        return HttpResponseRedirect(url)
    except Exception as e:
        logger.error(f"❌ Error generando URL presignada para {file_id}: {e}")
        return Response({"detail": "Error generando acceso al archivo."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
