from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser
from drf_spectacular.utils import extend_schema

from apps.users.models.user_model import User
from apps.users.api.repositories.user_repository import UserRepository
from apps.users.api.serializers.user_create_serializers import UserCreateSerializer
from apps.users.api.serializers.user_update_serializers import UserUpdateSerializer
from apps.users.api.serializers.user_detail_serializers import UserDetailSerializer

from apps.core.pagination import Pagination
from ...filters import UserFilter

from apps.users.docs.user_doc import (
    get_user_profile_doc,
    list_users_doc,
    create_user_doc,
    manage_user_doc
)


# --- Obtener perfil del usuario autenticado ---
@extend_schema(
    summary=get_user_profile_doc["summary"],
    description=get_user_profile_doc["description"],
    tags=get_user_profile_doc["tags"],
    operation_id=get_user_profile_doc["operation_id"],
    responses=get_user_profile_doc["responses"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    serializer = UserDetailSerializer(
        request.user,
        context={
            "request": request,
            "include_image_url": True
        }
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


# --- Listar usuarios con filtros y paginación ---
@extend_schema(
    summary=list_users_doc["summary"],
    description=list_users_doc["description"],
    tags=list_users_doc["tags"],
    operation_id=list_users_doc["operation_id"],
    parameters=list_users_doc["parameters"],
    responses=list_users_doc["responses"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_list_view(request):
    queryset = UserRepository.get_all_active_users().order_by('-created_at')
    filterset = UserFilter(request.GET, queryset=queryset)
    if not filterset.is_valid():
        return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

    paginator = Pagination()
    page = paginator.paginate_queryset(filterset.qs, request)
    serializer = UserDetailSerializer(page, many=True, context={"request": request, "include_image_url": True})
    return paginator.get_paginated_response(serializer.data)


# --- Crear nuevo usuario (admin-only) ---
@extend_schema(
    summary=create_user_doc["summary"],
    description=create_user_doc["description"],
    tags=create_user_doc["tags"],
    operation_id=create_user_doc["operation_id"],
    request=create_user_doc["request"],
    responses=create_user_doc["responses"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@parser_classes([MultiPartParser])
def user_create_view(request):
    serializer = UserCreateSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        user = serializer.save()
        response_data = UserDetailSerializer(user, context={"request": request, "include_image_url": True}).data
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- Gestionar usuario por ID (GET, PUT, DELETE) ---
@extend_schema(
    summary=manage_user_doc["summary"],
    description=manage_user_doc["description"],
    tags=manage_user_doc["tags"],
    operation_id=manage_user_doc["operation_id"],
    parameters=manage_user_doc["parameters"],
    responses=manage_user_doc["responses"]
)
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

        serializer = UserDetailSerializer(user_instance, context={"request": request, "include_image_url": True})
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        if not (is_admin or is_self):
            return Response({'detail': 'No tienes permiso para actualizar este usuario.'}, status=status.HTTP_403_FORBIDDEN)

        # Campos que un usuario común puede modificar
        if not is_admin:
            allowed_fields = {'name', 'last_name', 'dni', 'email', 'image'}
            for field in request.data:
                if field not in allowed_fields:
                    return Response(
                        {'detail': f'No puedes modificar el campo "{field}".'},
                        status=status.HTTP_403_FORBIDDEN
                    )

        serializer = UserUpdateSerializer(
            user_instance,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        if serializer.is_valid():
            updated_user = serializer.save()
            response_data = UserDetailSerializer(updated_user, context={"request": request, "include_image_url": True}).data
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if not is_admin:
            return Response({'detail': 'No tienes permiso para eliminar este usuario.'}, status=status.HTTP_403_FORBIDDEN)

        UserRepository.soft_delete(user_instance)
        return Response({'message': 'Usuario eliminado (soft) correctamente.'}, status=status.HTTP_200_OK)
