from celery import shared_task
from django.core.mail import send_mail
from apps.cuts.models.cutting_order_model import CuttingOrder

@shared_task
def send_cutting_order_assigned_email(cutting_order_id):
    cutting_order = CuttingOrder.objects.get(id=cutting_order_id)
    subject = f"Orden de corte asignada: {cutting_order.customer}"
    message = f"Has sido asignado a una nueva orden de corte para {cutting_order.customer} con una cantidad a cortar de {cutting_order.cutting_quantity} metros."
    recipient_list = [cutting_order.assigned_to.email]
    
    send_mail(subject, message, 'emanuel15diaz@gmail.com', recipient_list)
