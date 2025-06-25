from django.core.exceptions import ObjectDoesNotExist, ValidationError
from apps.products.models.product_model import Product
from apps.stocks.models.stock_product_model import ProductStock
import logging

logger = logging.getLogger(__name__)

class StockProductRepository:
    """
    Repositorio para ProductStock (stock de productos sin subproductos).
    Delega lógica de save/delete/auditoría a BaseModel.
    La lógica de negocio (ajustar stock + evento) debe estar en un Servicio.
    """

    # --- Métodos de Lectura ---
    @staticmethod
    def get_by_stock_id(stock_id: int) -> ProductStock | None:
        """Obtiene un registro de stock de producto activo por su ID de stock."""
        try:
            # select_related para optimizar acceso a product.name, etc.
            return ProductStock.objects.select_related('product', 'created_by', 'modified_by', 'deleted_by').get(id=stock_id, status=True)
        except ProductStock.DoesNotExist:
            return None

    @staticmethod
    def get_stock_for_product(product: Product) -> ProductStock | None:
        """
        Obtiene el registro de stock activo para un producto específico.
        Devuelve None si no existe o el producto es inválido.
        """
        if not isinstance(product, Product) or not product.pk:
             return None
        try:
             # Asume OneToOne o busca el único activo. Ajusta si un producto puede tener múltiples ProductStock activos.
            return ProductStock.objects.select_related('product', 'created_by', 'modified_by', 'deleted_by').get(product=product, status=True)
        except ProductStock.DoesNotExist:
            return None
        except ProductStock.MultipleObjectsReturned:
             # Decide cómo manejar este caso si puede ocurrir
             logger.info(
                 f"ALERTA: Múltiples ProductStock activos encontrados para Producto ID {product.pk}"
             )
             return ProductStock.objects.filter(product=product, status=True).first()


    @staticmethod
    def get_all_active():
        """Obtiene todos los registros de ProductStock activos."""
        # Ordenados por -created_at (de BaseModel)
        return ProductStock.objects.filter(status=True).select_related('product', 'created_by')

    # --- Método Create BÁSICO ---
    @staticmethod
    def create_stock(product: Product, quantity: float, user) -> ProductStock:
        """
        Crea un registro de ProductStock básico.
        La creación del StockEvent inicial debe manejarse en un Servicio/Transacción.
        """
        # Validación básica
        if quantity < 0:
            raise ValueError("La cantidad inicial no puede ser negativa.")
        if not isinstance(product, Product) or product.pk is None:
             raise ValueError("Se requiere una instancia de Producto válida.")
        # Validación extra: Asegurarse que este producto NO tenga subproductos?
        # if product.subproducts.exists():
        #     raise ValidationError("No se puede crear ProductStock para un producto con subproductos.")
        # Validación extra: Asegurarse que no exista ya un ProductStock si es OneToOne?
        # if ProductStock.objects.filter(product=product).exists():
        #      raise ValidationError(f"Ya existe un registro de stock para el producto {product.name}")

        stock = ProductStock(
            product=product,
            quantity=quantity            # created_by será asignado por save()
        )
        stock.save(user=user) # Delega a BaseModel
        return stock

    # --- Método Soft Delete ---
    @staticmethod
    def soft_delete_stock(stock_instance: ProductStock, user) -> ProductStock:
        """Realiza un soft delete usando la lógica de BaseModel.delete."""
        if not isinstance(stock_instance, ProductStock):
             raise ValueError("Se requiere una instancia de ProductStock válida.")
        stock_instance.delete(user=user) # Delega a BaseModel
        return stock_instance

    # --- NO HAY UPDATE GENÉRICO ---
    # Las actualizaciones de cantidad deben hacerse en métodos específicos
    # (ej. adjust_stock, receive_stock, dispatch_stock) en un Servicio o
    # Repositorio que también creen el StockEvent y usen transacciones.
