from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product  # Asegúrate de importar el modelo Product

User = get_user_model()

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')  # Relación de uno a muchos
    quantity = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateTimeField(auto_now=True)
    modified_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Stock for {self.product.name} on {self.date}'

    def update_stock(self, cut_length, reason, user):
        """
        Actualiza el stock al realizar un corte. El stock se reduce en función del `cut_length`.
        """
        if 'initial_length' not in self.product.metadata:
            raise ValueError("El producto no tiene `initial_length` en metadata.")

        # Stock antes de realizar el corte
        stock_before = self.product.metadata['initial_length']

        # Calcula el nuevo stock después del corte
        new_length = stock_before - cut_length
        if new_length < 0:
            raise ValueError("El corte excede la longitud disponible en el stock.")

        # Actualiza el `initial_length` en metadata del producto
        self.product.metadata['initial_length'] = new_length
        self.product.save()

        # Crea una nueva entrada en el historial de stock
        StockHistory.objects.create(
            product=self.product,
            stock_before=stock_before,
            stock_after=new_length,
            change_reason=reason,
            user=user
        )

    @staticmethod
    def get_total_stock():
        """
        Calcula el stock total sumando `initial_length` de todos los productos en el inventario.
        """
        total_stock = 0
        products_with_stock = Product.objects.filter(metadata__has_key='initial_length')
        for product in products_with_stock:
            total_stock += product.metadata.get('initial_length', 0)
        return total_stock


class StockHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_history')  # Relación con el producto
    stock_before = models.DecimalField(max_digits=15, decimal_places=2)  # Stock antes del cambio
    stock_after = models.DecimalField(max_digits=15, decimal_places=2)   # Stock después del cambio
    change_reason = models.TextField()  # Motivo del cambio
    recorded_at = models.DateTimeField(auto_now_add=True)  # Fecha del registro
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario que realizó el cambio

    def __str__(self):
        return f'History for {self.product.name} - Change at {self.recorded_at}'
