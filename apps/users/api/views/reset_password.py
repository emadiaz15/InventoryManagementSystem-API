from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.users.models import User

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_password_reset_email(request):
    """
    Envía un correo electrónico con un enlace único para cambiar la contraseña.
    """
    user = request.user  # Solo usuarios autenticados
    token_generator = PasswordResetTokenGenerator()

    # Generar un token único
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = request.build_absolute_uri(reverse('password_reset', args=[uid, token]))

    # Enviar email al usuario
    send_mail(
        subject="Password Reset Request",
        message=f"Use the following link to reset your password: {reset_url}",
        from_email="noreply@yourapp.com",
        recipient_list=[user.email],
    )

    return Response({'message': 'Password reset email sent successfully.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def password_reset_confirm(request, uidb64, token):
    """
    Permite cambiar la contraseña si el token es válido.
    """
    try:
        # Decodificar el ID del usuario
        user_id = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
        token_generator = PasswordResetTokenGenerator()

        # Validar token
        if not token_generator.check_token(user, token):
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        # Cambiar la contraseña
        new_password = request.data.get('password')
        if not new_password or len(new_password) < 8:
            return Response({'detail': 'Password must be at least 8 characters.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
