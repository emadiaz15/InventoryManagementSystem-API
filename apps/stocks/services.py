# services.py
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings

# Importa los modelos necesarios
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.models import ProductStock, SubproductStock, StockEvent

User = settings.AUTH_USER_MODEL

# ========================== FUNCIONES PARA PRODUCT STOCK (Productos sin subproductos) ==========================

@transaction.atomic
def initialize_product_stock(product: Product, user: User, 
                             initial_quantity: Decimal = Decimal('0.00'),
                             reason: str = "Stock Inicial por Creación") -> ProductStock:
    """
    Crea el registro ProductStock inicial para un producto y el evento de stock correspondiente.
    Lanza error si ya existe stock para esa combinación producto/ubicación.
    """
    if not isinstance(product, Product) or not product.pk:
        raise ValueError("Se requiere una instancia de Producto válida y guardada.")

    try:
        initial_quantity = Decimal(initial_quantity)
        if initial_quantity < 0:
            raise ValidationError("La cantidad inicial no puede ser negativa.")
    except (InvalidOperation, TypeError):
        raise ValidationError("La cantidad inicial debe ser un número válido.")

    # Verificar si ya existe un registro de stock para este producto y ubicación.
    query_params = {'product': product}
    existing_stock = ProductStock.objects.filter(**query_params).first()
    if existing_stock:
        raise ValueError(
            f"Ya existe stock para '{product.name}'. Use ajuste de stock."
        )

    stock_instance = ProductStock(
        product=product,
        quantity=initial_quantity
    )
    # Guardar usando BaseModel.save para asignar created_by
    stock_instance.save(user=user)

    # Crear el evento de stock inicial solo si hay cantidad > 0
    if initial_quantity > 0:
        StockEvent.objects.create(
            product_stock=stock_instance,
            subproduct_stock=None,
            quantity_change=initial_quantity,
            event_type='ingreso_inicial',
            created_by=user,
            notes=reason
        )

    print(f"--- Servicio: Stock inicial creado para Producto {product.pk} ---")
    return stock_instance


@transaction.atomic
def adjust_product_stock(product_stock: ProductStock, quantity_change: Decimal, 
                         reason: str, user: User) -> ProductStock:
    """
    Ajusta manualmente el stock de un ProductStock y crea un StockEvent.
    """
    if not isinstance(product_stock, ProductStock) or not product_stock.pk:
        raise ValueError("Se requiere una instancia de ProductStock válida.")

    try:
        quantity_change = Decimal(quantity_change)
        if quantity_change == 0:
            raise ValidationError("La cantidad del ajuste no puede ser cero.")
    except (InvalidOperation, TypeError):
        raise ValidationError("La cantidad del ajuste debe ser un número válido.")

    if (product_stock.quantity + quantity_change) < 0:
        raise ValidationError(
            f"Ajuste inválido. Stock resultante negativo para '{product_stock.product.name}'. Disponible: {product_stock.quantity}"
        )

    product_stock.quantity += quantity_change
    product_stock.save(user=user)

    StockEvent.objects.create(
        product_stock=product_stock,
        subproduct_stock=None,
        quantity_change=quantity_change,
        event_type='ingreso_ajuste' if quantity_change > 0 else 'egreso_ajuste',
        created_by=user,        
        notes=reason
    )
    print(f"--- Servicio: Stock ajustado para Producto {product_stock.product.pk} ---")
    return product_stock


# ========================== FUNCIONES PARA SUBPRODUCT STOCK ==========================

@transaction.atomic
def initialize_subproduct_stock(subproduct: Subproduct, user: User, 
                                initial_quantity: Decimal = Decimal('0.00'), 
                                reason: str = "Stock Inicial por Creación") -> SubproductStock:
    """
    Crea el registro SubproductStock inicial para un subproducto y el evento correspondiente.
    Lanza error si ya existe stock para esa combinación subproducto/ubicación.
    """
    if not isinstance(subproduct, Subproduct) or not subproduct.pk:
        raise ValueError("Se requiere una instancia de Subproducto válida y guardada.")

    try:
        initial_quantity = Decimal(initial_quantity)
        if initial_quantity < 0:
            raise ValidationError("La cantidad inicial no puede ser negativa.")
    except (InvalidOperation, TypeError):
        raise ValidationError("La cantidad inicial debe ser un número válido.")

    query_params = {'subproduct': subproduct}
    existing_stock = SubproductStock.objects.filter(**query_params).first()
    if existing_stock:
        raise ValueError(
            f"Ya existe stock para '{subproduct.name}'. Use ajuste de stock."
        )

    stock_instance = SubproductStock(
        subproduct=subproduct,
        quantity=initial_quantity
    )
    stock_instance.save(user=user)

    if initial_quantity > 0:
        StockEvent.objects.create(
            product_stock=None,
            subproduct_stock=stock_instance,
            quantity_change=initial_quantity,
            event_type='ingreso_inicial',
            created_by=user,
            notes=reason
        )
    print(f"--- Servicio: Stock inicial creado para Subproducto {subproduct.pk} ---")
    return stock_instance


@transaction.atomic
def adjust_subproduct_stock(subproduct_stock: SubproductStock, quantity_change: Decimal, 
                            reason: str, user: User) -> SubproductStock:
    """
    Ajusta manualmente el stock de un SubproductStock y crea un StockEvent.
    """
    if not isinstance(subproduct_stock, SubproductStock) or not subproduct_stock.pk:
        raise ValueError("Se requiere una instancia de SubproductStock válida.")

    try:
        quantity_change = Decimal(quantity_change)
        if quantity_change == 0:
            raise ValidationError("La cantidad del ajuste no puede ser cero.")
    except (InvalidOperation, TypeError):
        raise ValidationError("La cantidad del ajuste debe ser un número válido.")

    if (subproduct_stock.quantity + quantity_change) < 0:
        raise ValidationError(
            f"Ajuste inválido. Stock resultante negativo para '{subproduct_stock.subproduct.name}'. Disponible: {subproduct_stock.quantity}"
        )

    subproduct_stock.quantity += quantity_change
    subproduct_stock.save(user=user)

    StockEvent.objects.create(
        product_stock=None,
        subproduct_stock=subproduct_stock,
        quantity_change=quantity_change,
        event_type='ingreso_ajuste' if quantity_change > 0 else 'egreso_ajuste',
        created_by=user,
        notes=reason
    )
    print(f"--- Servicio: Stock ajustado para Subproducto {subproduct_stock.subproduct.pk} ---")
    return subproduct_stock


@transaction.atomic
def dispatch_subproduct_stock_for_cut(subproduct: Subproduct, cutting_quantity: Decimal,
                                      order_pk: int, user_performing_cut: User) -> SubproductStock:
    """
    Descuenta stock de un subproducto debido a una orden de corte y crea el evento.
    """
    if not isinstance(subproduct, Subproduct) or not subproduct.pk:
        raise ValueError("Se requiere una instancia de Subproducto válida.")
    try:
        cutting_quantity = Decimal(cutting_quantity)
        if cutting_quantity <= 0:
            raise ValidationError("La cantidad a cortar debe ser positiva.")
    except (InvalidOperation, TypeError):
        raise ValidationError("La cantidad a cortar debe ser un número válido.")
    
    if not user_performing_cut or not user_performing_cut.is_authenticated:
        raise ValueError("Se requiere un usuario válido para registrar el egreso por corte.")
    
    try:
        stock_to_update = SubproductStock.objects.select_for_update().get(
            subproduct=subproduct,
            status=True
        )
    except SubproductStock.DoesNotExist:
        raise ValidationError(f"No se encontró stock activo para '{subproduct.name}'.")
    except SubproductStock.MultipleObjectsReturned:
        raise ValidationError(f"Múltiples registros de stock encontrados para '{subproduct.name}'. Se requiere lógica adicional.")
    
    if cutting_quantity > stock_to_update.quantity:
        raise ValidationError(
            f"Stock insuficiente para corte de '{subproduct.name}'. Disponible: {stock_to_update.quantity}, Requerido: {cutting_quantity}"
        )
    
    stock_to_update.quantity -= cutting_quantity
    stock_to_update.save(user=user_performing_cut)
    
    StockEvent.objects.create(
        product_stock=None,
        subproduct_stock=stock_to_update,
        quantity_change=-cutting_quantity,
        event_type='egreso_corte',
        created_by=user_performing_cut,
        notes=f"Egreso por Orden de Corte #{order_pk}"
    )
    print(f"--- Servicio: Stock descontado por corte para Subproducto {subproduct.pk} ---")
    return stock_to_update


# ====================== FUNCIÓN DE VALIDACIÓN Y CORRECCIÓN GLOBAL ======================

def validate_and_correct_stock():
    """
    Recorre todos los productos y, para aquellos que tienen subproductos,
    ajusta el registro de stock (ProductStock) para que su cantidad coincida
    con la suma de las cantidades de sus subproductos.
    Se asume que cada producto tiene un ProductStock asociado a través del atributo 'stock_record'.
    """
    # Importa ProductStock desde su ubicación real
    from apps.stocks.models.stock_product_model import ProductStock

    for product in Product.objects.all():
        total_subproduct_quantity = Decimal('0.00')

        for subproduct in product.subproducts.all():
            total_subproduct_quantity += (
                SubproductStock.objects
                    .filter(subproduct=subproduct, status=True)
                    .aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
            )
        
        try:
            stock_record = product.stock_record
        except ProductStock.DoesNotExist:
            print(f"No existe registro de stock para el producto {product.name}")
            continue
        
        if stock_record.quantity != total_subproduct_quantity:
            print(f"Corrigiendo stock para el producto {product.name}")
            stock_record.quantity = total_subproduct_quantity
            stock_record.save()
            print(f"Stock del producto {product.name} actualizado a {stock_record.quantity}")

