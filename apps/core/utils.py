from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.conf import settings

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
