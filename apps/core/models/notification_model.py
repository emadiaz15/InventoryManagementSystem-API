from django.db import models
from apps.users.models import User
from apps.cuts.models.cutting_order_model import CuttingOrder

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    cutting_order = models.ForeignKey(CuttingOrder, on_delete=models.CASCADE)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

