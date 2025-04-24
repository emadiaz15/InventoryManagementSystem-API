import requests
from django.http import JsonResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from apps.users.services.images_services import delete_profile_image
from apps.users.models.user_model import User
from apps.users.docs.user_doc import image_delete_doc


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
    """Elimina una imagen de perfil del servicio FastAPI y limpia el campo en el modelo User."""
    if not file_id:
        raise Http404("Falta el ID del archivo")

    try:
        delete_profile_image(file_id, request.user.id)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            raise Http404("Imagen no encontrada en FastAPI.")
        raise Http404(f"No se pudo eliminar la imagen: {e}")

    # Limpia el campo en el modelo User si corresponde
    if request.user.image == file_id:
        request.user.image = None
        request.user.save(update_fields=["image"])

    return JsonResponse({"message": "Imagen eliminada correctamente."}, status=200)
