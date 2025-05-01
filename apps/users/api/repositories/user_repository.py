from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from apps.users.models.user_model import User
from django.conf import settings

class UserRepository:
    """
    Repositorio para User. Centraliza operaciones de lectura y escritura.
    Incluye restablecimiento de contraseña.
    """

    @staticmethod
    def get_all_active_users():
        """Obtiene todos los usuarios activos."""
        return User.objects.filter(is_active=True)

    @staticmethod
    def get_by_id(user_id: int) -> User | None:
        """Obtiene un usuario activo por su ID o None si no existe."""
        try:
            return User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return None

    @staticmethod
    def create(**kwargs) -> User:
        """Crea un nuevo usuario y devuelve la instancia."""
        password = kwargs.pop("password", None)
        user = User(**kwargs)
        if password:
            user.set_password(password)
        user.save()
        return user


    @staticmethod
    def update(user_instance: User, **kwargs) -> User:
        """
        Actualiza campos de un usuario existente.
        Acepta: username, email, name, last_name, dni, is_active, is_staff, password.
        """
        password = kwargs.pop('password', None)
        for attr, value in kwargs.items():
            setattr(user_instance, attr, value)
        if password:
            user_instance.set_password(password)
        user_instance.save()
        return user_instance

    @staticmethod
    def soft_delete(user_instance: User) -> User:
        """Realiza un soft delete (is_active=False) en el usuario."""
        user_instance.is_active = False
        user_instance.save(update_fields=['is_active'])
        return user_instance

    @staticmethod
    def generate_password_reset_token(user: User) -> str:
        """Genera un token único de restablecimiento de contraseña para el usuario."""
        generator = PasswordResetTokenGenerator()
        return generator.make_token(user)

    @staticmethod
    def build_password_reset_url(user: User, request) -> str:
        """Construye la URL completa para resetear contraseña."""
        token = UserRepository.generate_password_reset_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        path = reverse('password_reset_confirm', args=[uid, token])
        return request.build_absolute_uri(path)

    @staticmethod
    def send_password_reset_email(user: User, request, from_email: str = None):
        """Envía el correo con el enlace para restablecer contraseña."""
        if from_email is None:
            from_email or getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@yourapp.com")
        reset_url = UserRepository.build_password_reset_url(user, request)
        subject = 'Solicitud de restablecimiento de contraseña'
        message = f"Usa este enlace para cambiar tu contraseña:\n\n{reset_url}"
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[user.email],
            fail_silently=False,
        )

    @staticmethod
    def confirm_password_reset(uidb64: str, token: str, new_password: str) -> User:
        """Verifica el token y actualiza la contraseña del usuario."""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserRepository.get_by_id(int(uid))
            if user is None:
                raise ValidationError('Usuario no encontrado o inactivo.')
        except (TypeError, ValueError, OverflowError):
            raise ValidationError('UID inválido.')

        generator = PasswordResetTokenGenerator()
        if not generator.check_token(user, token):
            raise ValidationError('Token inválido o expirado.')

        if len(new_password) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')

        user.set_password(new_password)
        user.save()
        return user
