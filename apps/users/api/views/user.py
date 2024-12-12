from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from apps.users.models import User
from ..serializers import UserSerializer
from drf_spectacular.utils import extend_schema
from apps.core.pagination import Pagination

@extend_schema(
    operation_id="get_user_profile",
    description="Retrieve the profile of the authenticated user.",
    responses={
        200: UserSerializer,
        401: "Unauthorized - User not authenticated"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Endpoint to retrieve the authenticated user's profile.
    """
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@extend_schema(
    operation_id="list_users",
    description="Retrieve a list of all users. Only accessible by admin users.",
    responses={
        200: UserSerializer(many=True),
        403: "Forbidden - Not allowed to access"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])  # Only admins can access
def user_list_view(request):
    """
    Endpoint to retrieve a list of users with pagination, showing the newest users first.
    """
    paginator = Pagination()
    users = User.objects.filter(is_active=True).order_by('-created_at')
    result_page = paginator.paginate_queryset(users, request)
    serializer = UserSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@extend_schema(
    operation_id="create_user",
    description="Create a new user. Only accessible by admin users.",
    request=UserSerializer,
    responses={
        201: UserSerializer,
        400: "Bad Request - Invalid data",
        403: "Forbidden - Not allowed to access"
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_create_view(request):
    """
    Endpoint to create a new user (admin only).
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id="manage_user",
    description="Retrieve, update or soft-delete a specific user by ID.",
    request=UserSerializer,
    responses={
        200: UserSerializer,
        400: "Bad Request - Invalid data",
        404: "User not found",
        403: "Forbidden - Not allowed to access"
    }
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail_api_view(request, pk=None):
    """
    Endpoint to retrieve, update or soft-delete a specific user.
    - Staff users: can perform all CRUD operations (GET, PUT, DELETE).
    - Non-staff users: can only read (GET) and update (PUT).
    """
    user = get_object_or_404(User, id=pk, is_active=True)

    if request.method == 'GET':
        # Todos los usuarios autenticados pueden leer
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Todos los usuarios autenticados pueden actualizar
        serializer = UserSerializer(user, data=request.data, partial=True)  # Permite actualización parcial
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Solo usuarios staff pueden eliminar (borrado lógico)
        if not request.user.is_staff:
            return Response({'detail': 'You do not have permission to delete this user.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Soft delete: marcar el usuario como inactivo
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response({'message': 'User set to inactive successfully (soft delete).'}, status=status.HTTP_200_OK)
