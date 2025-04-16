from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def notify_assigned_cutting_order(user_id, cutting_order_id):
    """
    Tarea para notificar a un usuario que le fue asignada una orden de corte.
    Por ahora solo loguea la acción. Luego enviaremos un websocket u otro mecanismo.
    """
    logger.info(f"🔔 Notificar al usuario {user_id} sobre la orden de corte {cutting_order_id}")
    # Aquí podrías guardar una notificación en la base o enviar por WebSocket
