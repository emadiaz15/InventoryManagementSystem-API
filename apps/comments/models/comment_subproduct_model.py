from django.db import models
from apps.users.models import User
from apps.comments.models.base_model import BaseModel

from apps.products.models.subproduct_model import Subproduct


class SubproductComment(BaseModel):
    """Modelo para comentarios asociados a subproductos."""
    subproduct = models.ForeignKey(Subproduct, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

