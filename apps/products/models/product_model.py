from django.db import models
from django.db.models import Sum
from apps.products.models.category_model import Category
from apps.products.models.type_model import Type
from apps.products.models.base_model import BaseModel  
from apps.products.models.subproduct_model import Subproduct  
from apps.stocks.models.stock_event_model import StockEvent

class Product(BaseModel):
    """Modelo de Producto con relación a stock y subproductos."""
    
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.IntegerField(unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    status = models.BooleanField(default=True)  # Activo por defecto
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} ({self.code})'

    @property
    def total_stock(self):
        """
        Calcula el stock total sumando el stock del producto y el de sus subproductos.
        Optimización con `prefetch_related` para mejorar las consultas a la base de datos.
        """
        # Stock del producto principal
        product_stock = self.product_stock.quantity if self.product_stock else 0

        # Stock de los subproductos asociados
        subproduct_stock_total = Subproduct.objects.filter(parent=self, status=True).prefetch_related(
            'stocks'
        ).aggregate(total=Sum('stocks__quantity'))['total'] or 0

        return product_stock + subproduct_stock_total

    def update_stock(self, quantity_change, user, location=None):
        """
        Actualiza el stock del producto y de sus subproductos, registrando un evento de stock.
        """
        if quantity_change == 0:
            return

        # Actualizar el stock del producto principal
        if self.product_stock:
            self.product_stock.update_stock(quantity_change, user, location)

        # Actualizar el stock de los subproductos relacionados
        subproducts = Subproduct.objects.filter(parent=self)
        for subproduct in subproducts:
            if subproduct.stocks.exists():
                subproduct.update_stock(quantity_change, user, location)

        # Registrar un evento de stock para el producto principal
        StockEvent.objects.create(
            stock_instance=self.product_stock,
            quantity_change=quantity_change,
            user=user,
            location=location
        )

    @staticmethod
    def validate_code(code):
        """
        Valida que el código del producto sea un entero positivo y único.
        """
        if not isinstance(code, int) or code <= 0:
            raise ValueError("El código del producto debe ser un número entero positivo.")
        if Product.objects.filter(code=code).exists():
            raise ValueError("El código del producto ya está en uso.")

