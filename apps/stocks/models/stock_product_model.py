from django.db import models
from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product

class ProductStock(BaseModel): 
    """Stock para un Producto específico (que NO tiene subproductos)."""

    product = models.OneToOneField(  # Un registro de stock por producto
        Product,
        on_delete=models.CASCADE, 
        related_name='stock_record',
        verbose_name="Producto",
        limit_choices_to={'subproducts__isnull': True}
    )
    quantity = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="Cantidad Actual"
    )

    class Meta:
        verbose_name = "Stock de Producto"
        verbose_name_plural = "Stocks de Productos"
        # ordering = ['-created_at'] # Ya heredado

    def __str__(self):
        product_name = getattr(self.product, 'name', f'ID:{self.product_id}')
        return f"Stock de {product_name}: {self.quantity}"
