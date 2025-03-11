from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from apps.stocks.models import ProductStock
from apps.stocks.models import SubproductStock
from apps.stocks.models.stock_event_model import StockEvent
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.api.repositories.stock_product_repository import ProductRepository

class SubproductRepository:
    """
    Repositorio para gestionar el stock de subproductos y las operaciones relacionadas con subproductos.
    """

    @staticmethod
    def create_subproduct_stock(quantity, location, subproduct, user):
        """
        Crea un nuevo registro de stock para un subproducto.
        Registra un evento de tipo "entrada".
        """
        if quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

        if not location:
            raise ValidationError("Debe proporcionar una ubicación válida.")

        # Crear stock para el subproducto
        stock = SubproductStock(
            quantity=quantity,
            location=location,
            subproduct=subproduct,
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

        # Verificar si el stock de subproductos coincide con el stock del producto principal
        ProductRepository.validate_product_stock(subproduct.parent.id)

        return stock

    @staticmethod
    def update_subproduct_stock(stock, quantity_change, user, location=None):
        """
        Actualiza el stock de un subproducto y registra un evento de tipo "ajuste".
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

        # Verificar si el stock de subproductos coincide con el stock del producto principal
        ProductRepository.validate_product_stock(stock.subproduct.parent.id)

        return stock

    @staticmethod
    def delete_subproduct_stock(stock, user):
        """
        Realiza un soft delete de un registro de stock de subproducto.
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

        # Verificar si el stock de subproductos coincide con el stock del producto principal
        ProductRepository.validate_product_stock(stock.subproduct.parent.id)

        return stock

    @staticmethod
    def get_subproduct_stock(subproduct_id):
        """
        Obtiene el registro de stock de un subproducto específico.
        """
        return SubproductStock.objects.filter(subproduct__id=subproduct_id).select_related("subproduct").first()

    @staticmethod
    def validate_subproduct_stock(subproduct_id):
        """
        Valida que el stock de subproductos no sea mayor que el stock del producto principal.
        """
        subproduct_stock = SubproductStock.objects.filter(subproduct__id=subproduct_id).aggregate(
            total=models.Sum("quantity")
        )["total"] or 0

        subproduct = Subproduct.objects.get(id=subproduct_id)
        product_stock = ProductStock.objects.filter(product=subproduct.parent).aggregate(
            total=models.Sum("quantity")
        )["total"] or 0

        if subproduct_stock > product_stock:
            raise ValidationError(f"El stock total de los subproductos no puede superar el stock del producto principal (ID: {subproduct.parent.id}).")
