from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework.response import Response
from rest_framework import status
from django.utils.deprecation import MiddlewareMixin

class BlacklistAccessTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Verificar si existe el header de autorización con el token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            access_token_str = auth_header.split(' ')[1]
            try:
                # Decodificar el access token
                access_token = AccessToken(access_token_str)

                # Buscar el token en OutstandingToken (tokens generados)
                token_in_db = OutstandingToken.objects.filter(token=access_token_str).first()

                # Si el token existe y está en la blacklist, denegar acceso
                if token_in_db and BlacklistedToken.objects.filter(token=token_in_db).exists():
                    return Response(
                        {"detail": "Session expired or invalid token"},
                        status=status.HTTP_401_UNAUTHORIZED
                    )

            except Exception:
                # Si hay un error al decodificar el token, retornar 401
                return Response(
                    {"detail": "Invalid token"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return None