from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError

from apps.users.docs.user_doc import password_reset_confirm_doc
from apps.users.api.repositories.user_repository import UserRepository
from apps.users.api.serializers.password_reset_serializers import PasswordResetConfirmSerializer


@extend_schema(
    summary=password_reset_confirm_doc["summary"],
    description=password_reset_confirm_doc["description"],
    tags=password_reset_confirm_doc["tags"],
    operation_id=password_reset_confirm_doc["operation_id"],
    parameters=password_reset_confirm_doc["parameters"],
    request=password_reset_confirm_doc["request"],
    responses=password_reset_confirm_doc["responses"],
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def password_reset_confirm(request, uidb64: str, token: str):
    """
    🛠️ Permite a un administrador restablecer la contraseña de un usuario mediante token y uid.
    🔐 Seguridad: solo admins pueden usar este endpoint.
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    new_password = serializer.validated_data["password"]

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
