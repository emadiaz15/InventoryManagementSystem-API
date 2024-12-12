from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from apps.users.models import User
from ..serializers import UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema(
    operation_id="register_view",
    description="Register a new user (Staff only).",
    request=UserSerializer,
    responses={
        201: UserSerializer,
        400: "Bad Request - Invalid data",
        403: "Forbidden - You don't have permission to access this resource"
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])  # Solo staff puede registrar nuevos usuarios
def register_view(request):
    """
    View to register a new user.
    Only staff users can create new users.
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "user": UserSerializer(user).data,
            "message": "User created successfully. Now perform login to get your token."
        }, status=status.HTTP_201_CREATED)
    
    return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    post=extend_schema(
        operation_id="obtain_jwt_token_pair",
        description="Obtain JWT token pair (access and refresh)",
        request=CustomTokenObtainPairSerializer,
        responses={
            200: "JWT Token",
            400: "Bad Request - Invalid credentials"
        },
    )
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View to obtain a JWT token pair (access and refresh).
    Uses a custom serializer to add additional claims to the token.
    """
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    operation_id="logout_user",
    description="Logout a user by invalidating the refresh token",
    request={"type": "object", "properties": {"refresh_token": {"type": "string"}}},
    responses={
        205: "Token successfully invalidated",
        400: "Invalid token - Refresh token is required or invalid",
    },
)
class LogoutView(APIView):
    """
    View to log out a user by blacklisting the refresh token.
    Requires the refresh token to be provided, which will be invalidated.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Token successfully invalidated"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": f"Failed to invalidate token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
