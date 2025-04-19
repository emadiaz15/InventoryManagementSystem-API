from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
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


@extend_schema(**get_user_profile_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Endpoint para obtener el perfil del usuario autenticado.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**list_users_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_list_view(request):
    """
    Endpoint para listar todos los usuarios (solo admin), con filtros y paginación.
    """
    queryset = UserRepository.get_all_active_users().order_by('-created_at')
    filterset = UserFilter(request.GET, queryset=queryset)
    if not filterset.is_valid():
        return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
    queryset = filterset.qs

    paginator = Pagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = UserSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_user_doc)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_create_view(request):
    """
    Endpoint para que un admin cree un nuevo usuario.
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        # delegamos al serializer, que internamente setea contraseña y sube imagen si viene
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**manage_user_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail_view(request, pk=None):
    """
    Endpoint para:
    - GET: ver un usuario (solo staff o el propio usuario).  
    - PUT: actualizar (solo staff o el propio usuario).  
    - DELETE: dar de baja suave (solo staff).
    """
    # Usamos el repositorio para obtener o 404
    user_instance = UserRepository.get_by_id(pk)
    if not user_instance:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    # --- GET ---
    if request.method == 'GET':
        if request.user.is_staff or request.user.id == user_instance.id:
            return Response(
                UserSerializer(user_instance).data,
                status=status.HTTP_200_OK
            )
        return Response(
            {'detail': 'No tienes permiso para ver este perfil.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # --- PUT ---
    if request.method == 'PUT':
        if not (request.user.is_staff or request.user.id == user_instance.id):
            return Response(
                {'detail': 'No tienes permiso para actualizar este usuario.'},
                status=status.HTTP_403_FORBIDDEN
            )
        # Si no es staff, restringimos campos editables
        if not request.user.is_staff:
            allowed = {'name', 'last_name', 'dni', 'email', 'image'}
            for field in request.data:
                if field not in allowed:
                    return Response(
                        {'detail': f'No puedes modificar "{field}".'},
                        status=status.HTTP_403_FORBIDDEN
                    )
        serializer = UserSerializer(user_instance, data=request.data, partial=True)
        if serializer.is_valid():
            updated = serializer.save()
            return Response(
                UserSerializer(updated).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- DELETE (soft delete) ---
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response(
                {'detail': 'No tienes permiso para eliminar este usuario.'},
                status=status.HTTP_403_FORBIDDEN
            )
        UserRepository.soft_delete(user_instance)
        return Response(
            {'message': 'Usuario dado de baja correctamente.'},
            status=status.HTTP_200_OK
        )