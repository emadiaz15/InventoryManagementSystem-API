
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from drf_spectacular.utils import extend_schema
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
import logging

from apps.products.models import Product, ProductImage
from apps.products.services.product_image_services import (
    upload_product_file,
    list_product_files,
    delete_product_file,
    download_product_file,
)
from apps.products.api.repositories.product_file_repository import ProductFileRepository
from apps.products.docs.product_image_doc import (
    product_image_upload_doc,
    product_image_list_doc,
    product_image_delete_doc,
    product_image_download_doc
)
from apps.drive.utils.jwt_utils import extract_bearer_token

# Logger configurado
logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = getattr(settings, "ALLOWED_CONTENT_TYPES", set())

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
@permission_classes([IsAuthenticated])
def product_file_upload_view(request, product_id: str):
    # Validar existencia del producto
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

    token = extract_bearer_token(request, token_type="fastapi")
    results, errors = [], []
    for file in files:
        try:
            result = upload_product_file(file=file, product_id=product_id, token=token)
            file_id = result.get("file_id")

            if not file_id:
                raise ValueError("El microservicio no devolvió un 'file_id' válido.")

            if not ProductFileRepository.exists(int(product_id), file_id):
                ProductFileRepository.create(product_id=int(product_id), drive_file_id=file_id)

            results.append(file_id)

        except Exception as e:
            logger.error(f"❌ Error subiendo archivo {file.name}: {e}")
            errors.append({file.name: str(e)})

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
        token = extract_bearer_token(request, token_type="fastapi")
        files = list_product_files(product_id=product_id, token=token)
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
@permission_classes([IsAuthenticated])
def product_file_delete_view(request, product_id: str, file_id: str):
    get_object_or_404(Product, pk=product_id)

    try:
        if not ProductFileRepository.exists(int(product_id), file_id):
            return Response({"detail": "El archivo no está asociado a este producto."}, status=status.HTTP_404_NOT_FOUND)

        token = extract_bearer_token(request, token_type="fastapi")
        delete_product_file(product_id=product_id, file_id=file_id, token=token)
        ProductFileRepository.delete(file_id=file_id)
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
    try:
        product_id = int(product_id)
    except ValueError:
        return Response({"detail": "ID de producto inválido."}, status=status.HTTP_400_BAD_REQUEST)

    get_object_or_404(Product, pk=product_id)
    force_download = request.query_params.get("force", "false").lower() == "true"

    if not force_download and not ProductFileRepository.exists(product_id, file_id):
        raise Http404(f"🛑 Archivo {file_id} no está vinculado al producto {product_id}")

    try:
        token = extract_bearer_token(request, token_type="fastapi")
        content, filename, content_type = download_product_file(product_id, file_id, token)
        response = HttpResponse(content, content_type=content_type)
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
    except Exception as e:
        logger.error(f"❌ Error descargando archivo {file_id} de producto {product_id}: {e}")
        return Response({"detail": f"No se pudo descargar el archivo: {str(e)}"}, status=status.HTTP_404_NOT_FOUND)