import logging
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from apps.users.models.user_model import User
from apps.storages_client.services.profile_image import delete_profile_image
from django.conf import settings

logger = logging.getLogger(__name__)

class UserRepository:
    """
    Repositorio para User. Centraliza operaciones de lectura y escritura.
    Incluye restablecimiento de contraseña.
    """

    @staticmethod
    def get_all_active_users():
        return User.objects.filter(is_active=True)

    @staticmethod
    def get_by_id(user_id: int) -> User | None:
        try:
            return User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return None

    @staticmethod
    def create(**kwargs) -> User:
        password = kwargs.pop("password", None)
        user = User(**kwargs)
        if password:
            user.set_password(password)
        user.save()
        logger.info(f"✅ Usuario creado: {user.id} - {user.username}")
        return user

    @staticmethod
    def update(user_instance: User, **kwargs) -> User:
        password = kwargs.pop('password', None)

        for attr, value in kwargs.items():
            if attr in ['id', 'pk']:
                continue  # No permitir modificar ID
            setattr(user_instance, attr, value)

        if password:
            user_instance.set_password(password)

        user_instance.save()
        logger.info(f"✏️ Usuario actualizado: {user_instance.id} - {user_instance.username}")
        return user_instance

    @staticmethod
    def soft_delete(user_instance: User) -> User:
        """Soft delete + elimina imagen de perfil si existe."""
        if user_instance.image:
            try:
                delete_profile_image(user_instance.image, user_instance.id)
                logger.info(f"🗑️ Imagen de perfil eliminada para usuario {user_instance.id}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo eliminar imagen de perfil: {e}")

        user_instance.is_active = False
        user_instance.image = None
        user_instance.save(update_fields=['is_active', 'image'])
        logger.info(f"🚫 Usuario desactivado: {user_instance.id} - {user_instance.username}")
        return user_instance

    @staticmethod
    def generate_password_reset_token(user: User) -> str:
        return PasswordResetTokenGenerator().make_token(user)

    @staticmethod
    def build_password_reset_url(user: User, request) -> str:
        token = UserRepository.generate_password_reset_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        path = reverse('password_reset_confirm', args=[uid, token])
        return request.build_absolute_uri(path)

    @staticmethod
    def send_password_reset_email(user: User, request, from_email: str = None):
        if from_email is None:
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@yourapp.com")

        reset_url = UserRepository.build_password_reset_url(user, request)
        subject = 'Solicitud de restablecimiento de contraseña'
        message = f"Usa este enlace para cambiar tu contraseña:\n\n{reset_url}"

        send_mail(subject, message, from_email, [user.email], fail_silently=False)
        logger.info(f"✉️ Email de recuperación enviado a {user.email}")

    @staticmethod
    def confirm_password_reset(uidb64: str, token: str, new_password: str) -> User:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserRepository.get_by_id(int(uid))
            if user is None:
                raise ValidationError('Usuario no encontrado o inactivo.')
        except (TypeError, ValueError, OverflowError):
            raise ValidationError('UID inválido.')

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise ValidationError('Token inválido o expirado.')

        if len(new_password) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')

        user.set_password(new_password)
        user.save()
        logger.info(f"🔑 Contraseña restablecida para usuario {user.id}")
        return user
