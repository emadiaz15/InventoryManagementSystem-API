import os
import django
from django.core.mail import send_mail

# Configurar Django si ejecutas fuera de un entorno gestionado (como el servidor de Django)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings.local')
django.setup()

# Prueba de envío de correo
def send_test_email():
    subject = "Prueba de envío de correo"
    message = "Este es un mensaje de prueba enviado desde Django."
    from_email = os.getenv("EMAIL_HOST_USER")  # Tu correo configurado en el .env
    recipient_list = ["e.diaz@itecriocuarto.org.ar"]  # Cambia por tu correo de prueba

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print("Correo enviado con éxito.")
    except Exception as e:
        print(f"Error al enviar correo: {e}")

if __name__ == "__main__":
    send_test_email()
