from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser

from drf_spectacular.utils import extend_schema

from django.shortcuts import get_object_or_404

from apps.users.models.user_model import User
from apps.users.api.repositories.user_repository import UserRepository
from ..serializers.user_serializers import UserSerializer
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
    serializer = UserSerializer(
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
    """Endpoint para listar todos los usuarios (solo admin), con filtros y paginación."""
    queryset = UserRepository.get_all_active_users().order_by('-created_at')
    filterset = UserFilter(request.GET, queryset=queryset)
    if not filterset.is_valid():
        return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
    queryset = filterset.qs

    paginator = Pagination()
    page = paginator.paginate_queryset(queryset, request)
    # 👇 Importante: se desactiva carga base64 para lista
    serializer = UserSerializer(page, many=True, context={"request": request, "include_image_url": True})
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
@parser_classes([MultiPartParser])  # 👈 para soporte de imagen
def user_create_view(request):
    """Endpoint para que un admin cree un nuevo usuario y cargue imagen (opcional)."""
    serializer = UserSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user, context={"request": request}).data, status=status.HTTP_201_CREATED)
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
@parser_classes([MultiPartParser])  # 👈 necesario para PUT con imagen
def user_detail_view(request, pk=None):
    """
    Endpoint para:
    - GET: ver un usuario (solo staff o el propio usuario).  get
    - PUT: actualizar (solo staff o el propio usuario).  
    - DELETE: dar de baja suave (solo staff).
    """
    user_instance = UserRepository.get_by_id(pk)
    if not user_instance:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if request.user.is_staff or request.user.id == user_instance.id:
            serializer = UserSerializer(
                user_instance,
                context={
                    "request": request,
                    "include_image_url": True
                }
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': 'No tienes permiso para ver este perfil.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        if not (request.user.is_staff or request.user.id == user_instance.id):
            return Response({'detail': 'No tienes permiso para actualizar este usuario.'}, status=status.HTTP_403_FORBIDDEN)

        if not request.user.is_staff:
            allowed = {'name', 'last_name', 'dni', 'email', 'image'}
            for field in request.data:
                if field not in allowed:
                    return Response(
                        {'detail': f'No puedes modificar "{field}".'},
                        status=status.HTTP_403_FORBIDDEN
                    )
        serializer = UserSerializer(user_instance, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            updated = serializer.save()
            return Response(UserSerializer(updated, context={"request": request}).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({'detail': 'No tienes permiso para eliminar este usuario.'}, status=status.HTTP_403_FORBIDDEN)
        UserRepository.soft_delete(user_instance)
        return Response({'message': 'Usuario dado de baja correctamente.'}, status=status.HTTP_200_OK)
