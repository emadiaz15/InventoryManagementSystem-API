import logging
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema

from ..serializers.user_token_serializers import CustomTokenObtainPairSerializer
from apps.users.docs.user_doc import (
    obtain_jwt_token_pair_doc,
    logout_user_doc
)

logger = logging.getLogger(__name__)


@extend_schema(
    summary=obtain_jwt_token_pair_doc["summary"],
    description=obtain_jwt_token_pair_doc["description"],
    tags=obtain_jwt_token_pair_doc["tags"],
    operation_id=obtain_jwt_token_pair_doc["operation_id"],
    request=obtain_jwt_token_pair_doc["request"],
    responses=obtain_jwt_token_pair_doc["responses"],
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Obtiene un par de tokens JWT (access y refresh).
    """
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    summary=logout_user_doc["summary"],
    description=logout_user_doc["description"],
    tags=logout_user_doc["tags"],
    operation_id=logout_user_doc["operation_id"],
    request=logout_user_doc["request"],
    responses=logout_user_doc["responses"],
)
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

        if refresh_token.count('.') != 2:
            logger.warning("Token de logout con formato inválido.")
            return self._neutral_response()

        try:
            token = RefreshToken(refresh_token)

            if token.token_type != "refresh":
                logger.warning("Token proporcionado no es de tipo refresh.")
                return self._neutral_response()

            token.blacklist()
            return self._neutral_response()

        except TokenError:
            logger.warning("Token inválido o expirado durante logout.")
            return self._neutral_response()

        except Exception as e:
            logger.error(f"Error inesperado al cerrar sesión: {e}")
            return Response(
                {"error": "Error interno al procesar la solicitud."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @staticmethod
    def _neutral_response():
        """
        Respuesta genérica para ocultar si el token es inválido o ya expiró.
        """
        return Response(
            {"message": "Sesión finalizada."},
            status=status.HTTP_205_RESET_CONTENT
        )
