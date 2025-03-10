from django.db import models
from .base_model import BaseModel
from .category_model import Category

class Type(BaseModel):
    """✅ Modelo de Tipo reutilizando lógica de BaseModel"""
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name='types', null=True
    )
