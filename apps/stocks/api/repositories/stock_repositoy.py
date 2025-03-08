from apps.stocks.models.stock_model import Stock

from django.db import models

class StockRepository:
    """Repositorio para manejar la lógica de acceso a los datos de Stock."""

    @staticmethod
    def create_stock(quantity, location, product=None, subproduct=None, user=None):
        """Crea un nuevo registro de stock para un producto o subproducto."""
        if not product and not subproduct:
            raise ValueError("Debe proporcionar un producto o subproducto.")
        
        stock = Stock(
            quantity=quantity,
            location=location,
            product=product,
            subproduct=subproduct,
            created_by=user  # Asignamos el usuario creador
        )
        stock.save(user=user)  # Guarda el stock con el usuario que lo creó
        return stock

    @staticmethod
    def update_stock(stock, quantity_change, user, location=None):
        """Actualiza la cantidad de stock y registra un evento de movimiento."""
        # Actualizamos el stock usando el método 'update_stock' del modelo
        stock.update_stock(quantity_change, user, location)
    
    @staticmethod
    def get_stock_by_product(product_id):
        """Obtiene el stock de un producto específico."""
        try:
            return Stock.objects.get(product__id=product_id)
        except Stock.DoesNotExist:
            return None

    @staticmethod
    def get_stock_by_subproduct(subproduct_id):
        """Obtiene el stock de un subproducto específico."""
        try:
            return Stock.objects.get(subproduct__id=subproduct_id)
        except Stock.DoesNotExist:
            return None

    @staticmethod
    def get_all_stocks():
        """Obtiene todos los registros de stock."""
        return Stock.objects.all()

    @staticmethod
    def delete_stock(stock, user):
        """Realiza un soft delete de un registro de stock."""
        stock.delete(user=user)
        stock.modified_by = user  # Asignamos el usuario que realiza el soft delete
        stock.modified_at = models.DateTimeField(auto_now=True)  # Se registra la fecha de modificación
        stock.save()
