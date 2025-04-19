# apps/users/api/views/auth.py

import logging
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema_view, extend_schema

from ..serializers.user_serializers import CustomTokenObtainPairSerializer
from apps.users.docs.user_doc import (
    obtain_jwt_token_pair_doc,
    logout_user_doc
)

logger = logging.getLogger(__name__)

@extend_schema_view(
    post=extend_schema(**obtain_jwt_token_pair_doc)
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Obtiene un par de tokens JWT (access y refresh).
    """
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(**logout_user_doc)
class LogoutView(APIView):
    """
    Cierra sesión invalidando el refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "Se requiere el refresh_token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            if token.token_type != "refresh":
                return Response(
                    {"error": "El token proporcionado no es un refresh token."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token.blacklist()
            return Response(
                {"message": "Refresh token invalidado correctamente."},
                status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError:
            logger.warning("Intento de logout con token inválido o expirado.")
            return Response(
                {"error": "Refresh token inválido o expirado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error inesperado en logout: {e}")
            return Response(
                {"error": "Error interno al invalidar el token."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
