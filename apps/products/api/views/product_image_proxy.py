import requests
from django.http import JsonResponse, Http404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser
from drf_spectacular.utils import extend_schema
from requests.exceptions import RequestException

from apps.products.services.product_image_services import (
    upload_product_image,
    list_product_images,
    delete_product_image,
)

from apps.products.docs.product_image_doc import (
    list_product_images_doc,
    upload_product_image_doc,
    delete_product_image_doc,
)

from apps.products.utils import safe_request

@extend_schema(
    summary=list_product_images_doc["summary"],
    description=list_product_images_doc["description"],
    tags=list_product_images_doc["tags"],
    operation_id=list_product_images_doc["operation_id"],
    parameters=list_product_images_doc["parameters"],
    responses=list_product_images_doc["responses"]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_image_list_view(request, product_id: str):
    """
    Lista las imágenes asociadas a un producto específico.
    """
    if not product_id:
        raise Http404("Falta el ID del producto.")

    images = safe_request(list_product_images, product_id)

    return JsonResponse({"images": images}, status=200)


@extend_schema(
    summary=upload_product_image_doc["summary"],
    description=upload_product_image_doc["description"],
    tags=upload_product_image_doc["tags"],
    operation_id=upload_product_image_doc["operation_id"],
    parameters=upload_product_image_doc["parameters"],
    request=upload_product_image_doc["requestBody"],
    responses=upload_product_image_doc["responses"]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
@parser_classes([MultiPartParser])
def product_image_upload_view(request, product_id: str):
    """
    Sube una imagen para un producto.
    """
    if not product_id:
        raise Http404("Falta el ID del producto.")

    file = request.FILES.get('file')
    if not file:
        return JsonResponse({"detail": "Falta el archivo."}, status=400)

    result = safe_request(upload_product_image, file, product_id)

    return JsonResponse(result, status=201)


@extend_schema(
    summary=delete_product_image_doc["summary"],
    description=delete_product_image_doc["description"],
    tags=delete_product_image_doc["tags"],
    operation_id=delete_product_image_doc["operation_id"],
    parameters=delete_product_image_doc["parameters"],
    responses=delete_product_image_doc["responses"]
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def product_image_delete_view(request, product_id: str, file_id: str):
    """
    Elimina una imagen específica de un producto.
    """
    if not product_id or not file_id:
        raise Http404("Faltan parámetros necesarios.")

    safe_request(delete_product_image, product_id, file_id)

    return JsonResponse({"message": "Imagen eliminada correctamente."}, status=200)
