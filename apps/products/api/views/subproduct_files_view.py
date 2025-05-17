from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.conf import settings
from drf_spectacular.utils import extend_schema
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
import logging

from apps.products.models import Product, Subproduct
from apps.products.api.repositories.subproduct_file_repository import SubproductFileRepository
from apps.products.services.subproduct_image_service import (
    upload_subproduct_file,
    list_subproduct_files,
    delete_subproduct_file,
    download_subproduct_file,
)
from apps.products.api.serializers.subproduct_image_serializer import SubproductImageSerializer
from apps.products.docs.subproduct_image_doc import (
    subproduct_image_upload_doc,
    subproduct_image_list_doc,
    subproduct_image_download_doc,
    subproduct_image_delete_doc,
)
from apps.drive.utils.jwt_utils import extract_bearer_token

logger = logging.getLogger(__name__)
ALLOWED_CONTENT_TYPES = getattr(settings, "ALLOWED_CONTENT_TYPES", set())

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

    token = extract_bearer_token(request, token_type="fastapi")
    results, errors = [], []

    for file in files:
        try:
            result = upload_subproduct_file(file=file, product_id=product_id, subproduct_id=subproduct_id, token=token)
            file_id = result.get("file_id")
            if not file_id:
                raise ValueError("El microservicio no devolvió un 'file_id' válido.")

            if not SubproductFileRepository.exists(int(subproduct_id), file_id):
                SubproductFileRepository.create(subproduct_id=int(subproduct_id), drive_file_id=file_id)

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
        queryset = SubproductFileRepository.get_all_by_subproduct(subproduct_id)
        serialized = SubproductImageSerializer(queryset, many=True)
        return Response({"files": serialized.data}, status=status.HTTP_200_OK)
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
        token = extract_bearer_token(request, token_type="fastapi")
        content, filename, content_type = download_subproduct_file(product_id, subproduct_id, file_id, token)
        response = HttpResponse(content, content_type=content_type)
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
    except Exception as e:
        logger.error(f"❌ Error descargando archivo {file_id} de subproducto {subproduct_id}: {e}")
        return Response({"detail": f"No se pudo descargar el archivo: {str(e)}"}, status=status.HTTP_404_NOT_FOUND)

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
        token = extract_bearer_token(request, token_type="fastapi")
        delete_subproduct_file(product_id=product_id, subproduct_id=subproduct_id, file_id=file_id, token=token)
        SubproductFileRepository.delete(file_id=file_id)
        return Response({"detail": "Archivo eliminado correctamente."}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"❌ Error eliminando archivo {file_id} de subproducto {subproduct_id}: {e}")
        return Response({"detail": f"Error eliminando archivo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
