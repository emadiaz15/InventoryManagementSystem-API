from apps.cuts.tasks import notify_cut_assignment

def send_cut_assignment_notification(user_id: int, cut_order_id: int):
    """
    Llama a la task Celery para enviar notificación asincrónica al operario asignado.
    """
    notify_cut_assignment.delay(user_id=user_id, cut_order_id=cut_order_id)
