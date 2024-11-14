# Este archivo define los modelos para gestionar el stock de productos y subproductos, así como el historial de cambios en el stock.

from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product, SubProduct  # Asegúrate de importar el modelo SubProduct

User = get_user_model()

class Stock(models.Model):
    """
    Modelo que representa el stock de un `Product` o `SubProduct` en el inventario.
    Puede asociarse opcionalmente a un `Product` o un `SubProduct` y mantiene el registro
    de la cantidad actual y el usuario que hizo la modificación.
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='stocks', null=True, blank=True,
        help_text="Referencia opcional al producto principal."
    )
    subproduct = models.ForeignKey(
        SubProduct, on_delete=models.CASCADE, related_name='stocks', null=True, blank=True,
        help_text="Referencia opcional al subproducto específico."
    )
    quantity = models.DecimalField(max_digits=15, decimal_places=2, help_text="Cantidad actual de stock.")
    date = models.DateTimeField(auto_now=True, help_text="Fecha y hora del último cambio en el stock.")
    modified_at = models.DateTimeField(auto_now=True, help_text="Fecha y hora de la última modificación.")
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Usuario que realizó el ajuste de stock.")
    is_active = models.BooleanField(default=True, help_text="Indica si el stock está activo (eliminación suave).")

    def __str__(self):
        # Identifica si es un subproducto o producto y devuelve una descripción adecuada
        if self.subproduct:
            return f'Stock for {self.subproduct.name} (SubProduct) on {self.date}'
        return f'Stock for {self.product.name} on {self.date}'

    def update_stock(self, cut_length, reason, user):
        """
        Actualiza el stock al realizar un ajuste de longitud (`cut_length`).
        Si el stock se asocia a un `SubProduct`, utiliza esa longitud;
        si no, se considera la longitud de `Product`.
        """
        stock_before = self.quantity

        # Calcula el nuevo stock después del ajuste
        new_quantity = stock_before - cut_length
        if new_quantity < 0:
            raise ValueError("El corte excede la longitud disponible en el stock.")

        # Guarda el nuevo stock y registra el cambio en el historial
        self.quantity = new_quantity
        self.save()

        # Crea una nueva entrada en el historial de stock
        StockHistory.objects.create(
            product=self.product,
            subproduct=self.subproduct,
            stock_before=stock_before,
            stock_after=new_quantity,
            change_reason=reason,
            user=user
        )

    def soft_delete(self, reason, user):
        """
        Elimina de manera suave el stock marcando el campo `is_active` como False
        y registra el cambio en el historial.
        """
        # Registra la cantidad de stock antes de eliminar
        stock_before = self.quantity

        # Marca el stock como inactivo
        self.is_active = False
        self.quantity = 0  # Opcional: Establece la cantidad en 0 para indicar que no hay stock activo
        self.save()

        # Registra la eliminación en el historial de stock
        StockHistory.objects.create(
            product=self.product,
            subproduct=self.subproduct,
            stock_before=stock_before,
            stock_after=0,
            change_reason=reason or "Eliminación suave de stock",
            user=user
        )

    @staticmethod
    def get_total_stock():
        """
        Calcula el stock total sumando las cantidades de stock de todos los `Product` y `SubProduct` activos.
        """
        total_stock = Stock.objects.filter(is_active=True).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
        return total_stock


class StockHistory(models.Model):
    """
    Modelo que representa el historial de cambios de stock, almacenando detalles de cada
    ajuste, el stock antes y después del cambio, y el motivo del ajuste.
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='stock_history', null=True, blank=True,
        help_text="Producto al que se asocia el ajuste de stock."
    )
    subproduct = models.ForeignKey(
        SubProduct, on_delete=models.CASCADE, related_name='stock_history', null=True, blank=True,
        help_text="Subproducto al que se asocia el ajuste de stock, si aplica."
    )
    stock_before = models.DecimalField(max_digits=15, decimal_places=2, help_text="Cantidad de stock antes del ajuste.")
    stock_after = models.DecimalField(max_digits=15, decimal_places=2, help_text="Cantidad de stock después del ajuste.")
    change_reason = models.TextField(help_text="Motivo del ajuste de stock.")
    recorded_at = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora del ajuste de stock.")
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Usuario que realizó el ajuste.")

    def __str__(self):
        # Describe si el ajuste fue realizado en un subproducto o producto
        if self.subproduct:
            return f'History for {self.subproduct.name} (SubProduct) - Change at {self.recorded_at}'
        return f'History for {self.product.name} - Change at {self.recorded_at}'
