from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def notify_cut_assignment(user_id: int, cut_order_id: int):
    """
    Task que notifica al usuario que se le asignó una nueva orden de corte.
    Este evento puede ser enviado luego por WebSocket o guardado en un modelo de notificaciones.
    """
    logger.info(f"🔔 Notificar asignación de orden {cut_order_id} al usuario {user_id}")
    # Aquí se puede agregar lógica como guardar en base de datos, enviar por WebSocket, etc.

@shared_task
def notify_cut_status_change(user_id: int, cut_order_id: int, new_status: str):
    """
    Task que notifica al usuario que el estado de su orden ha cambiado.
    """
    logger.info(f"🔄 Notificar cambio de estado de la orden {cut_order_id} a '{new_status}' para el usuario {user_id}")
    # Aquí se puede agregar lógica como guardar en base de datos, enviar por WebSocket, etc.
