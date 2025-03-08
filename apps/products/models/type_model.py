from django.db import models
from apps.products.models.base_model import BaseModel
from apps.products.models.category_model import Category

class Type(BaseModel):
    """Modelo de Tipo reutilizando lógica de BaseModel"""
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='types', null=False, default=1
    )
    name = models.CharField(max_length=255, unique=True)  # Campo para el nombre del tipo
    description = models.TextField(blank=True, null=True)  # Campo para la descripción del tipo

    def __str__(self):
        return self.name  # Retorna el nombre del tipo como representación
