import logging
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.products.api.repositories.subproduct_file_repository import SubproductFileRepository
from apps.products.services.subproduct_image_service import (
    upload_subproduct_file,
    list_subproduct_files,
    delete_subproduct_file,
    download_subproduct_file,
)
from apps.drive.utils.jwt_utils import extract_bearer_token
from apps.products.docs.subproduct_image_doc import (
    subproduct_image_upload_doc,
    subproduct_image_list_doc,
    subproduct_image_download_doc,
    subproduct_image_delete_doc,
)

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = getattr(settings, "ALLOWED_CONTENT_TYPES", set())

@extend_schema(
    tags=subproduct_image_upload_doc["tags"],
    summary=subproduct_image_upload_doc["summary"],
    operation_id=subproduct_image_upload_doc["operation_id"],
    description=subproduct_image_upload_doc["description"],
    parameters=subproduct_image_upload_doc["parameters"],
    request=subproduct_image_upload_doc["requestBody"],
    responses=subproduct_image_upload_doc["responses"]
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def subproduct_file_upload_view(request, product_id: str, subproduct_id: str):
    # Asegurar que el padre exista y esté activo
    get_object_or_404(Product, pk=product_id, status=True)
    get_object_or_404(Subproduct, pk=subproduct_id, parent_id=product_id, status=True)

    files = request.FILES.getlist("file")
    if not files:
        return Response({"detail": "No se proporcionaron archivos."}, status=status.HTTP_400_BAD_REQUEST)

    invalid = [f.name for f in files if f.content_type not in ALLOWED_CONTENT_TYPES]
    if invalid:
        return Response(
            {"detail": f"Tipo no permitido en: {', '.join(invalid)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    token = extract_bearer_token(request, token_type="fastapi")
    uploaded, errors = [], []

    for f in files:
        try:
            result = upload_subproduct_file(
                file=f,
                product_id=product_id,
                subproduct_id=subproduct_id,
                token=token
            )
            file_id = result.get("file_id")
            if not file_id:
                raise ValueError("No se recibió file_id desde FastAPI")
            uploaded.append(file_id)
        except Exception as e:
            logger.error(f"Error subiendo {f.name}: {e}")
            errors.append({f.name: str(e)})

    status_code = status.HTTP_201_CREATED if uploaded and not errors else (
        status.HTTP_207_MULTI_STATUS if uploaded and errors else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response({"uploaded": uploaded, "errors": errors or None}, status=status_code)


@extend_schema(
    tags=subproduct_image_list_doc["tags"],
    summary=subproduct_image_list_doc["summary"],
    operation_id=subproduct_image_list_doc["operation_id"],
    description=subproduct_image_list_doc["description"],
    parameters=subproduct_image_list_doc["parameters"],
    responses=subproduct_image_list_doc["responses"]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subproduct_file_list_view(request, product_id: str, subproduct_id: str):
    get_object_or_404(Product, pk=product_id, status=True)
    get_object_or_404(Subproduct, pk=subproduct_id, parent_id=product_id, status=True)

    token = extract_bearer_token(request, token_type="fastapi")
    try:
        files = list_subproduct_files(
            product_id=product_id,
            subproduct_id=subproduct_id,
            token=token
        )
        return Response({"files": files}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error listando archivos de subproducto {subproduct_id}: {e}")
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=subproduct_image_download_doc["tags"],
    summary=subproduct_image_download_doc["summary"],
    operation_id=subproduct_image_download_doc["operation_id"],
    description=subproduct_image_download_doc["description"],
    parameters=subproduct_image_download_doc["parameters"],
    responses=subproduct_image_download_doc["responses"]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subproduct_file_download_view(request, product_id: str, subproduct_id: str, file_id: str):
    get_object_or_404(Product, pk=product_id, status=True)
    get_object_or_404(Subproduct, pk=subproduct_id, parent_id=product_id, status=True)

    if not SubproductFileRepository.exists(int(subproduct_id), file_id):
        raise Http404("Archivo no asociado a este subproducto")

    token = extract_bearer_token(request, token_type="fastapi")
    try:
        content = download_subproduct_file(
            product_id=product_id,
            subproduct_id=subproduct_id,
            file_id=file_id,
            token=token
        )
        # La FastAPI ya establece inline/disposition, aquí devolvemos bytes
        return HttpResponse(content, content_type="application/octet-stream")
    except Exception as e:
        logger.error(f"Error descargando archivo {file_id}: {e}")
        raise Http404(str(e))


@extend_schema(
    tags=subproduct_image_delete_doc["tags"],
    summary=subproduct_image_delete_doc["summary"],
    operation_id=subproduct_image_delete_doc["operation_id"],
    description=subproduct_image_delete_doc["description"],
    parameters=subproduct_image_delete_doc["parameters"],
    responses=subproduct_image_delete_doc["responses"]
)
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def subproduct_file_delete_view(request, product_id: str, subproduct_id: str, file_id: str):
    get_object_or_404(Product, pk=product_id, status=True)
    get_object_or_404(Subproduct, pk=subproduct_id, parent_id=product_id, status=True)

    if not SubproductFileRepository.exists(int(subproduct_id), file_id):
        return Response({"detail": "Archivo no vinculado a este subproducto."}, status=status.HTTP_404_NOT_FOUND)

    token = extract_bearer_token(request, token_type="fastapi")
    try:
        delete_subproduct_file(
            product_id=product_id,
            subproduct_id=subproduct_id,
            file_id=file_id,
            token=token
        )
        SubproductFileRepository.delete(file_id=file_id)
        return Response({"detail": "Archivo eliminado correctamente."}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error eliminando archivo {file_id}: {e}")
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
