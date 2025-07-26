# apps/products/api/views/subproduct_files_view.py

from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
import logging

from apps.products.models import Product, Subproduct
from apps.products.api.repositories.subproduct_file_repository import SubproductFileRepository
from apps.storages_client.services.subproducts_files import (
    upload_subproduct_file,
    delete_subproduct_file,
    get_subproduct_file_url
)
from apps.products.docs.subproduct_image_doc import (
    subproduct_image_upload_doc,
    subproduct_image_list_doc,
    subproduct_image_download_doc,
    subproduct_image_delete_doc,
)
from apps.products.utils.cache_helpers_subproducts import (
    SUBPRODUCT_LIST_CACHE_PREFIX,
    subproduct_detail_cache_key
)
from apps.products.utils.redis_utils import delete_keys_by_pattern  # añadimos la utilidad

logger = logging.getLogger(__name__)
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}


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
    get_object_or_404(Product, pk=product_id, status=True)
    get_object_or_404(Subproduct, pk=subproduct_id, parent_id=product_id, status=True)

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
    for f in files:
        try:
            res = upload_subproduct_file(
                file=f,
                product_id=int(product_id),
                subproduct_id=int(subproduct_id),
            )
            SubproductFileRepository.create(
                subproduct_id=int(subproduct_id),
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
        # 1) invalidar TODAS las páginas cacheadas de lista de subproductos
        delete_keys_by_pattern(f"{SUBPRODUCT_LIST_CACHE_PREFIX}*")
        # 2) invalidar caché de detalle concreto
        cache.delete(subproduct_detail_cache_key(product_id, subproduct_id))

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
    get_object_or_404(Product, pk=product_id, status=True)
    get_object_or_404(Subproduct, pk=subproduct_id, parent_id=product_id, status=True)

    try:
        files = SubproductFileRepository.get_all_by_subproduct(int(subproduct_id))
        return Response({
            "files": [
                {"key": f.key, "name": f.name, "mimeType": f.mime_type, "url": f.get_presigned_url()}
                for f in files
            ]
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"❌ Error listando archivos de subproducto {subproduct_id}: {e}")
        return Response({"detail": f"Error listando archivos: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    get_object_or_404(Product, pk=product_id, status=True)
    get_object_or_404(Subproduct, pk=subproduct_id, parent_id=product_id, status=True)

    if not SubproductFileRepository.exists(int(subproduct_id), file_id):
        raise Http404(f"🛑 Archivo {file_id} no está vinculado al subproducto {subproduct_id}")

    try:
        url = get_subproduct_file_url(file_id)
        return HttpResponseRedirect(url)
    except Exception as e:
        logger.error(f"❌ Error generando URL presignada para archivo {file_id} del subproducto {subproduct_id}: {e}")
        return Response({"detail": "Error generando acceso al archivo."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    get_object_or_404(Product, pk=product_id, status=True)
    get_object_or_404(Subproduct, pk=subproduct_id, parent_id=product_id, status=True)

    if not SubproductFileRepository.exists(int(subproduct_id), file_id):
        return Response({"detail": "El archivo no está vinculado a este subproducto."}, status=status.HTTP_404_NOT_FOUND)

    try:
        delete_subproduct_file(file_id)
        SubproductFileRepository.delete(file_id)
        # 1) invalidar TODAS las páginas cacheadas de lista de subproductos
        delete_keys_by_pattern(f"{SUBPRODUCT_LIST_CACHE_PREFIX}*")
        # 2) invalidar caché de detalle concreto
        cache.delete(subproduct_detail_cache_key(product_id, subproduct_id))
        return Response({"detail": "Archivo eliminado correctamente."}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"❌ Error eliminando archivo {file_id} de subproducto {subproduct_id}: {e}")
        return Response({"detail": f"Error eliminando archivo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
