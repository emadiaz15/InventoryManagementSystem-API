from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from apps.users.models import User
from ..serializers import UserSerializer
from drf_spectacular.utils import extend_schema
from ...pagination import CustomPagination

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
    paginator = CustomPagination()
    # Verificar si la consulta devuelve correctamente los usuarios más nuevos primero
    users = User.objects.all().order_by('-created_at')  # Orden explícito por fecha de creación descendente
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
    description="Retrieve, update or delete a specific user by ID. Accessible by authenticated users.",
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
    Endpoint to retrieve, update or delete a specific user.
    """
    user = get_object_or_404(User, id=pk)
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)  # Permitir actualización parcial
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)
