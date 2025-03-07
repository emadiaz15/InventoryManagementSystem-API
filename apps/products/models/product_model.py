from django.db import models
from django.db.models import Sum

from apps.products.models.category_model import Category
from apps.products.models.type_model import Type
from apps.products.models.base_model import BaseModel  # Importa la clase base

class Product(BaseModel):
    """Modelo de Producto reutilizando lógica de BaseModel con validación de código único."""
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.IntegerField(unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    status = models.BooleanField(default=True)  # Activo por defecto
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    type = models.ForeignKey(Type, related_name='products', on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subproducts'
    )

    # Relación con comentarios
    comments = models.ManyToManyField('comments.Comment', related_name='product_comments', blank=True)

    def __str__(self):
        return f'{self.name} ({self.code})'

    # Propiedad para calcular el stock total, sumando stock propio + el de los subproductos
    @property
    def total_stock(self):
        """Calcula el stock total sumando el propio + el de los subproductos"""
        # Stock del producto principal
        product_stock = self.stocks.filter(is_active=True).aggregate(total=Sum('quantity'))['total'] or 0

        # Stock de los subproductos
        subproduct_stock = self.subproducts.filter(status=True).annotate(sub_stock=Sum('stocks__quantity'))
        subproduct_stock_total = subproduct_stock.aggregate(total=Sum('sub_stock'))['total'] or 0

        return product_stock + subproduct_stock_total

    @staticmethod
    def validate_code(code):
        """Validación del código del producto"""
        if not isinstance(code, int) or code <= 0:
            raise ValueError("El código del producto debe ser un número entero positivo.")
