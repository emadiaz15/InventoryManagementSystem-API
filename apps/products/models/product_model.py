from django.db import models
from django.core.files.base import ContentFile
from django.db.models import Sum
from .category_model import Category
from .type_model import Type

class Product(models.Model):
    """Modelo de Producto reutilizando lógica de BaseModel con validación de código único."""
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.IntegerField(unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    status = models.BooleanField(default=True)  # Activo por defecto
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subproducts'
    )

    # Relación con comentarios
    comments = models.ManyToManyField('comments.Comment', related_name='product_comments', blank=True)

    @staticmethod
    def validate_code(code):
        """Validación del código del producto"""
        if not isinstance(code, int) or code <= 0:
            raise ValueError("El código del producto debe ser un número entero positivo.")

    @property
    def total_stock(self):
        """Calcula el stock total sumando el propio + el de los subproductos"""
        product_stock = self.stocks.filter(is_active=True).aggregate(total=Sum('quantity'))['total'] or 0
        subproduct_stock = self.subproducts.filter(status=True).annotate(sub_stock=Sum('stocks__quantity'))
        subproduct_stock_total = subproduct_stock.aggregate(total=Sum('sub_stock'))['total'] or 0
        return product_stock + subproduct_stock_total

    def __str__(self):
        return f'{self.name} ({self.code})'
