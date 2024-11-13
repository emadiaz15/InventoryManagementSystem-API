from django.core.mail import send_mail

def send_welcome_email(user):
    send_mail(
        'Welcome!',
        'Thank you for signing up.',
        'from@example.com',
        [user.email],
        fail_silently=False,
    )
    
# Puedes implementar un sistema de notificaciones que sea reutilizable en todo el proyecto, 
# como enviar correos electrónicos, notificaciones push o SMS.
