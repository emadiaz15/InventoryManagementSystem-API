from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from apps.users.models import User
from ..serializers import UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, extend_schema_view
import logging

# Configuración del logger para errores
logger = logging.getLogger(__name__)

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
    Vista para registrar un nuevo usuario.
    Solo los usuarios con permisos de staff pueden crear nuevos usuarios.
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
    Vista para obtener un par de tokens JWT (access y refresh).
    Usa un serializer personalizado para agregar claims adicionales al token.
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
    Vista para cerrar sesión de un usuario invalidando el refresh token.
    Requiere que se proporcione el refresh token, el cual será invalidado.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)

            # Validar que el token sea de tipo 'refresh'
            if token.token_type != "refresh":
                return Response({"error": "Provided token is not a refresh token"}, status=status.HTTP_400_BAD_REQUEST)

            # Invalidar el token
            token.blacklist()
            return Response({"message": "Token successfully invalidated"}, status=status.HTTP_205_RESET_CONTENT)

        except TokenError as e:
            logger.error(f"Logout failed for token: {refresh_token} | Error: {str(e)}")
            return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error during logout: {str(e)}")
            return Response({"error": f"Failed to invalidate token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
