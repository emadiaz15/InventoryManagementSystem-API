from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from apps.users.models.user_model import User
from ..serializers.user_serializers import UserSerializer
from drf_spectacular.utils import extend_schema
from apps.core.pagination import Pagination
from ...filters import UserFilter  # Asegúrate de que la ruta sea la correcta

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
    description="Retrieve a list of all users with filtering and pagination. Only accessible by admin users.",
    responses={
        200: UserSerializer(many=True),
        403: "Forbidden - Not allowed to access"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_list_view(request):
    """
    Endpoint to retrieve a list of users with pagination, showing the newest users first.
    Filters are applied via query parameters using the UserFilter.
    """
    # Initialize the queryset (order by newest first)
    queryset = User.objects.all().order_by('-created_at')
    # Apply the filters using django-filter's UserFilter
    filterset = UserFilter(request.GET, queryset=queryset)
    if not filterset.is_valid():
        return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
    queryset = filterset.qs

    paginator = Pagination()
    result_page = paginator.paginate_queryset(queryset, request)
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
    - Non-staff users: can only read (GET) their own profile.
    """
    user = get_object_or_404(User, id=pk, is_active=True)

    if request.method == 'GET':
        if request.user.is_staff or request.user.id == user.id:
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': 'You do not have permission to view this profile.'}, status=status.HTTP_403_FORBIDDEN)
    
    elif request.method == 'PUT':
        if not request.user.is_staff and request.user.id != user.id:
            return Response({'detail': 'You do not have permission to update this user.'}, status=status.HTTP_403_FORBIDDEN)
        
        if not request.user.is_staff:
            allowed_fields = {'name', 'last_name', 'dni', 'email', 'image'}
            for field in request.data.keys():
                if field not in allowed_fields:
                    return Response({'detail': f'You cannot modify the field "{field}".'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({'detail': 'You do not have permission to delete this user.'}, status=status.HTTP_403_FORBIDDEN)
        
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response({'message': 'User set to inactive successfully (soft delete).'}, status=status.HTTP_200_OK)
    