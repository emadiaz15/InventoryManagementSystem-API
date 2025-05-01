import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.users.services.profile_image_services import delete_profile_image, replace_profile_image
from apps.users.docs.user_doc import image_delete_doc, image_replace_doc


@extend_schema(
    summary=image_replace_doc["summary"],
    description=image_replace_doc["description"],
    tags=image_replace_doc["tags"],
    operation_id=image_replace_doc["operation_id"],
    parameters=image_replace_doc["parameters"],
    request=image_replace_doc["request"],
    responses=image_replace_doc["responses"]
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def image_replace_view(request, file_id: str):
    """
    Reemplaza una imagen de perfil existente del usuario autenticado
    con una nueva imagen proporcionada.
    """
    user = request.user

    if not file_id or not user.image:
        return JsonResponse({"detail": "No tienes imagen actual para reemplazar."}, status=status.HTTP_400_BAD_REQUEST)

    if str(user.image) != str(file_id):
        return JsonResponse({"detail": "No tienes permiso para modificar esta imagen."}, status=status.HTTP_403_FORBIDDEN)

    new_file = request.FILES.get("file")
    if not new_file:
        return JsonResponse({"detail": "Archivo requerido."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = replace_profile_image(new_file, file_id, user.id)
        user.image = result.get("file_id")
        user.save(update_fields=["image"])
        return JsonResponse({
            "message": "Imagen reemplazada correctamente.",
            "file_id": user.image
        }, status=status.HTTP_200_OK)
    except requests.HTTPError as e:
        return JsonResponse({
            "detail": f"Error HTTP al reemplazar la imagen: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JsonResponse({
            "detail": f"Error inesperado al reemplazar la imagen: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary=image_delete_doc["summary"],
    description=image_delete_doc["description"],
    tags=image_delete_doc["tags"],
    operation_id=image_delete_doc["operation_id"],
    parameters=image_delete_doc["parameters"],
    responses=image_delete_doc["responses"]
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def image_delete_view(request, file_id: str):
    """
    Elimina la imagen de perfil del usuario autenticado desde FastAPI
    y limpia el campo `image` en el modelo `User`.
    """
    user = request.user

    if not file_id:
        return JsonResponse({"detail": "Falta el ID de la imagen."}, status=status.HTTP_400_BAD_REQUEST)

    if not user.image:
        return JsonResponse({"detail": "El usuario no tiene imagen asociada."}, status=status.HTTP_400_BAD_REQUEST)

    if str(user.image) != str(file_id):
        return JsonResponse({"detail": "No tienes permiso para eliminar esta imagen."}, status=status.HTTP_403_FORBIDDEN)

    try:
        delete_profile_image(file_id, user.id)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return JsonResponse({"detail": "Imagen no encontrada en el servicio externo."}, status=status.HTTP_404_NOT_FOUND)
        return JsonResponse({"detail": f"Error HTTP al eliminar la imagen: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JsonResponse({"detail": f"Error inesperado al eliminar la imagen: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user.image = None
    user.save(update_fields=["image"])

    return JsonResponse({"message": "Imagen eliminada correctamente."}, status=status.HTTP_200_OK)
