import logging
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.users.models.user_model import User
from apps.users.api.repositories.user_repository import UserRepository
from apps.users.api.serializers.user_create_serializers import UserCreateSerializer
from apps.users.api.serializers.user_update_serializers import UserUpdateSerializer
from apps.users.api.serializers.user_detail_serializers import UserDetailSerializer
from apps.storages_client.services.profile_image import (
    delete_profile_image,
    replace_profile_image,
)
from apps.core.pagination import Pagination
from ...filters import UserFilter
from apps.users.docs.user_doc import (
    get_user_profile_doc, list_users_doc, create_user_doc,
    manage_user_doc, image_delete_doc, image_replace_doc
)

logger = logging.getLogger(__name__)

@extend_schema(**get_user_profile_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    serializer = UserDetailSerializer(
        request.user,
        context={"request": request, "include_image_url": True}
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**list_users_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_list_view(request):
    queryset = UserRepository.get_all_active_users().order_by('-created_at')
    filterset = UserFilter(request.GET, queryset=queryset)
    if not filterset.is_valid():
        return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

    paginator = Pagination()
    page = paginator.paginate_queryset(filterset.qs, request)
    serializer = UserDetailSerializer(
        page,
        many=True,
        context={"request": request, "include_image_url": True}
    )
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_user_doc)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@parser_classes([MultiPartParser])
def user_create_view(request):
    serializer = UserCreateSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        user = serializer.save()
        response_data = UserDetailSerializer(
            user,
            context={"request": request, "include_image_url": True}
        ).data
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**manage_user_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def user_detail_view(request, pk=None):
    user_instance = UserRepository.get_by_id(pk)
    if not user_instance:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    is_self = request.user.id == user_instance.id
    is_admin = request.user.is_staff

    if request.method == 'GET':
        if not (is_admin or is_self):
            return Response({'detail': 'No tienes permiso para ver este perfil.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserDetailSerializer(
            user_instance,
            context={"request": request, "include_image_url": True}
        )
        return Response(serializer.data)

    if request.method == 'PUT':
        if not (is_admin or is_self):
            return Response({'detail': 'No tienes permiso para actualizar este usuario.'}, status=status.HTTP_403_FORBIDDEN)

        if not is_admin:
            allowed_fields = {'name', 'last_name', 'dni', 'email', 'image'}
            for field in request.data:
                if field not in allowed_fields:
                    return Response({'detail': f'No puedes modificar el campo "{field}".'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserUpdateSerializer(
            user_instance,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        if serializer.is_valid():
            updated_user = serializer.save()
            response_data = UserDetailSerializer(
                updated_user,
                context={"request": request, "include_image_url": True}
            ).data
            return Response(response_data, headers={"X-Invalidate-Users-Cache": "true"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if not is_admin:
            return Response({'detail': 'No tienes permiso para eliminar este usuario.'}, status=status.HTTP_403_FORBIDDEN)

        if user_instance.image:
            try:
                delete_profile_image(user_instance.image, user_instance.id)
                user_instance.image = None
                user_instance.save(update_fields=["image"])
            except Exception as e:
                logger.warning(f"⚠️ Error al eliminar imagen de perfil: {e}")

        UserRepository.soft_delete(user_instance)
        return Response(
            {'message': 'Usuario eliminado (soft) correctamente y su imagen también.'},
            headers={"X-Invalidate-Users-Cache": "true"}
        )


@extend_schema(**image_replace_doc)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def image_replace_view(request, file_id: str):
    target_user = request.user
    if request.user.is_staff:
        user_id_param = request.GET.get("user_id")
        if not user_id_param:
            return Response({"detail": "Falta el parámetro user_id."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target_user = User.objects.get(id=user_id_param)
        except User.DoesNotExist:
            return Response({"detail": "Usuario destino no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if not file_id or not target_user.image:
        return Response({"detail": "No hay imagen para reemplazar."}, status=status.HTTP_400_BAD_REQUEST)

    if str(target_user.image) != str(file_id):
        return Response({"detail": "El ID de imagen no coincide con el usuario."}, status=status.HTTP_403_FORBIDDEN)

    new_file = request.FILES.get("file")
    if not new_file:
        return Response({"detail": "Archivo requerido."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = replace_profile_image(new_file, file_id, target_user.id)
        target_user.image = result.get("key")
        target_user.save(update_fields=["image"])
        # devolver la URL actualizada
        data = UserDetailSerializer(
            target_user,
            context={"request": request, "include_image_url": True}
        ).data
        return Response(data, headers={"X-Invalidate-Users-Cache": "true"})
    except Exception as e:
        logger.warning(f"Error al reemplazar imagen: {e}")
        return Response({"detail": "Error al reemplazar imagen."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(**image_delete_doc)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def image_delete_view(request, file_id: str):
    requester = request.user
    user_id = request.query_params.get("user_id")

    if requester.is_staff and user_id:
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Usuario objetivo no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    else:
        user = requester

    if not file_id:
        return Response({"detail": "Falta el ID de la imagen."}, status=status.HTTP_400_BAD_REQUEST)

    if not user.image:
        return Response({"detail": "El usuario no tiene imagen asociada."}, status=status.HTTP_400_BAD_REQUEST)

    if str(user.image) != str(file_id):
        return Response({"detail": "No tienes permiso para eliminar esta imagen."}, status=status.HTTP_403_FORBIDDEN)

    try:
        delete_profile_image(file_id, user.id)
    except Exception as e:
        logger.warning(f"Error al eliminar imagen: {e}")
        return Response({"detail": "Error al eliminar imagen."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user.image = ""
    user.save(update_fields=["image"])
    # devolvemos la nueva representación sin imagen
    data = UserDetailSerializer(
        user,
        context={"request": request, "include_image_url": True}
    ).data
    return Response(data, headers={"X-Invalidate-Users-Cache": "true"})
