from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

from apps.stocks.models import ProductStock
from apps.stocks.models.stock_event_model import StockEvent
from apps.products.models.product_model import Product

class ProductRepository:
    """
    Repositorio para gestionar el stock de productos y las operaciones relacionadas con los productos.
    """

    @staticmethod
    def create_product_stock(quantity, location, product, user):
        """
        Crea un nuevo registro de stock para un producto.
        Registra un evento de tipo "entrada".
        """
        if quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

        if not location:
            raise ValidationError("Debe proporcionar una ubicación válida.")

        # Crear stock para el producto
        stock = ProductStock(
            quantity=quantity,
            location=location,
            product=product,
            created_by=user
        )
        stock.save()

        # Registrar un evento de stock (entrada)
        StockEvent.objects.create(
            stock=stock,
            quantity_change=quantity,
            event_type="entrada",
            user=user,
            location=location
        )

        return stock

    @staticmethod
    def update_product_stock(stock, quantity_change, user, location=None):
        """
        Actualiza el stock de un producto y registra un evento de tipo "ajuste".
        Verifica que la cantidad de stock no sea negativa.
        """
        if stock.quantity + quantity_change < 0:
            raise ValidationError("No puede haber una cantidad negativa de stock.")

        # Actualizar la cantidad del stock
        stock.quantity += quantity_change
        stock.modified_by = user
        stock.modified_at = timezone.now()

        if location:
            stock.location = location

        stock.save()

        # Registrar un evento de stock (ajuste)
        StockEvent.objects.create(
            stock=stock,
            quantity_change=quantity_change,
            event_type="ajuste" if quantity_change != 0 else "entrada",
            user=user,
            location=location or stock.location
        )

        return stock

    @staticmethod
    def delete_product_stock(stock, user):
        """
        Realiza un soft delete de un registro de stock de producto.
        Actualiza el campo 'deleted_at' y 'modified_by', y registra un evento de salida.
        """
        stock.deleted_at = timezone.now()
        stock.modified_by = user
        stock.save()

        # Registrar un evento de salida
        StockEvent.objects.create(
            stock=stock,
            quantity_change=-stock.quantity,
            event_type="salida",
            user=user,
            location=stock.location
        )

        return stock

    @staticmethod
    def get_product_stock(product_id):
        """
        Obtiene el registro de stock de un producto específico.
        """
        return ProductStock.objects.filter(product__id=product_id).select_related("product").first()

    @staticmethod
    def validate_product_stock(product_id):
        """
        Valida que el stock de productos no sea negativo y que la cantidad total del stock sea coherente.
        """
        product_stock = ProductStock.objects.filter(product__id=product_id).aggregate(
            total=models.Sum("quantity")
        )["total"] or 0

        if product_stock < 0:
            raise ValidationError(f"El stock total del producto (ID: {product_id}) es negativo.")
