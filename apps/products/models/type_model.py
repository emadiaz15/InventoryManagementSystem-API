from django.db import models
from apps.products.models.base_model import BaseModel
from apps.products.models.category_model import Category

class Type(BaseModel):
    """✅ Modelo de Tipo reutilizando lógica de BaseModel"""
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='types', null=False, default=1
    )
