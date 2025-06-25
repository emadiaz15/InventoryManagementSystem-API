from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

User = get_user_model()

def send_assignment_notification(cutting_order):
    """
    Envia un email a los usuarios con rol "admin" y al usuario asignado
    notificando el estado de la orden de corte.
    """
    # Obtener todos los usuarios con rol de "admin"
    admin_users = User.objects.filter(is_staff=True)

    # Obtener el usuario asignado
    assigned_user = cutting_order.operator

    # Lista de destinatarios, excluyendo duplicados
    recipient_emails = list(set([user.email for user in admin_users if user.email] + [assigned_user.email]))

    # Renderizar el contenido del email
    subject = f"Asignación de Orden de Corte #{cutting_order.pk} - Estado: {cutting_order.status}"
    message = render_to_string('core/cutting_order_notification_email.html', {'cutting_order': cutting_order})

    # Enviar el email a todos los destinatarios
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_emails,
        fail_silently=False,
    )
    
@receiver(post_save, sender=User)
def send_new_user_notification(sender, instance, created, **kwargs):
    """
    Envía una notificación por correo electrónico a los administradores
    cada vez que se crea un nuevo usuario.
    """
    if created:
        # Obtenemos todos los administradores
        admin_users = User.objects.filter(is_staff=True)
        recipient_emails = [admin.email for admin in admin_users if admin.email]

        # Asunto y contenido del correo
        subject = f"Nuevo Usuario Creado: {instance.username}"
        message = render_to_string('core/new_user_notification_email.html', {'user': instance})

        # Enviamos el correo a todos los administradores
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_emails,
            fail_silently=False,
        )
        
        

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def send_new_user_notification(sender, instance, created, **kwargs):
    if created:
        logger.info("Iniciando envío de notificación por correo electrónico")
        admin_users = User.objects.filter(is_staff=True)
        recipient_emails = [admin.email for admin in admin_users if admin.email]

        subject = f"Nuevo Usuario Creado: {instance.username}"
        message = render_to_string('core/new_user_notification_email.html', {'user': instance})

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_emails,
                fail_silently=False,
            )
            logger.info("Correo enviado exitosamente")
        except Exception as e:
            logger.error(f"Error al enviar correo: {e}")
