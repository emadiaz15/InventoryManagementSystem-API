from django.db import models
from apps.products.models.base_model import BaseModel

class Category(BaseModel):
    """Modelo de Categoría reutilizando lógica de BaseModel"""
    name = models.CharField(max_length=255, unique=True)  # Campo para el nombre de la categoría
    description = models.TextField(blank=True, null=True)  # Campo para la descripción de la categoría

    def __str__(self):
        return self.name  # Retorna el nombre de la categoría como representación
