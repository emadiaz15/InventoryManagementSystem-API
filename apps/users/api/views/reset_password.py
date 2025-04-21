from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.exceptions import ValidationError

from apps.users.docs.user_doc import (
    send_password_reset_email_doc,
    password_reset_confirm_doc
)
from apps.users.api.repositories.user_repository import UserRepository

# --- Send password reset email ---
@extend_schema_view(
    post=extend_schema(
        summary=send_password_reset_email_doc["summary"],
        description=send_password_reset_email_doc["description"],
        tags=send_password_reset_email_doc["tags"],
        operation_id=send_password_reset_email_doc["operation_id"],
        responses=send_password_reset_email_doc["responses"]
    )
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_password_reset_email(request):
    """
    Envía un correo electrónico con un enlace único para cambiar la contraseña.
    """
    try:
        UserRepository.send_password_reset_email(request.user, request)
        return Response(
            {'message': 'Se ha enviado un correo para restablecer la contraseña.'},
            status=status.HTTP_200_OK
        )
    except ValidationError as e:
        detail = e.detail if hasattr(e, 'detail') else str(e)
        return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response(
            {'detail': 'Error interno al enviar el correo de restablecimiento.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# --- Confirm password reset ---
@extend_schema_view(
    post=extend_schema(
        summary=password_reset_confirm_doc["summary"],
        description=password_reset_confirm_doc["description"],
        tags=password_reset_confirm_doc["tags"],
        operation_id=password_reset_confirm_doc["operation_id"],
        parameters=password_reset_confirm_doc["parameters"],
        request=password_reset_confirm_doc["request"],
        responses=password_reset_confirm_doc["responses"]
    )
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request, uidb64: str, token: str):
    """
    Permite cambiar la contraseña si el token es válido.
    """
    new_password = request.data.get('password')
    if not new_password:
        return Response(
            {'detail': 'Se requiere la nueva contraseña.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        UserRepository.confirm_password_reset(uidb64, token, new_password)
        return Response(
            {'message': 'Contraseña restablecida correctamente.'},
            status=status.HTTP_200_OK
        )
    except ValidationError as e:
        detail = e.detail if hasattr(e, 'detail') else str(e)
        return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response(
            {'detail': 'Error interno al restablecer la contraseña.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
