from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings

from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.models import ProductStock, SubproductStock, StockEvent 

User = settings.AUTH_USER_MODEL

# --- FUNCIONES PARA PRODUCT STOCK (Productos sin subproductos) ---

@transaction.atomic # Asegura que todo ocurra o nada
def initialize_product_stock(product: Product, user: User, initial_quantity: Decimal = Decimal('0.00'), location: str = None, reason: str = "Stock Inicial por Creación") -> ProductStock:
    """
    Crea el registro ProductStock inicial para un producto y el evento de stock correspondiente.
    Lanza error si ya existe stock para esa combinación producto/ubicación.
    """
    if not isinstance(product, Product) or not product.pk:
        raise ValueError("Se requiere una instancia de Producto válida y guardada.")
    # Validar cantidad inicial (no negativa)
    try:
        initial_quantity = Decimal(initial_quantity) # Asegurar que sea Decimal
        if initial_quantity < 0:
            raise ValidationError("La cantidad inicial no puede ser negativa.")
    except (InvalidOperation, TypeError):
         raise ValidationError("La cantidad inicial debe ser un número válido.")

    # Verificar si ya existe stock para este producto/ubicación
    # Asume que la combinación producto/ubicación debe ser única si location no es None
    query_params = {'product': product, 'location': location}
    existing_stock = ProductStock.objects.filter(**query_params).first()
    if existing_stock:
        raise ValueError(f"Ya existe stock para '{product.name}' en la ubicación '{location or 'N/A'}'. Use ajuste de stock.")

    # 1. Crear el registro ProductStock
    stock_instance = ProductStock(
        product=product,
        quantity=initial_quantity,
        location=location
    )
    # Guardar usando BaseModel.save para asignar created_by
    stock_instance.save(user=user)

    # 2. Crear el evento de stock inicial (solo si la cantidad es > 0)
    if initial_quantity > 0:
        StockEvent.objects.create(
            product_stock=stock_instance, # FK a ProductStock
            subproduct_stock=None,
            quantity_change=initial_quantity,
            event_type='ingreso_inicial',
            user=user, # Usuario que crea el evento (heredado por BaseModel)
            location=stock_instance.location,
            notes=reason
            # created_by del evento también se asigna por BaseModel
        )
    # También podrías crear un evento tipo 'creacion_stock' si initial_quantity es 0

    print(f"--- Servicio: Stock inicial creado para Producto {product.pk} ---")
    return stock_instance

@transaction.atomic
def adjust_product_stock(product_stock: ProductStock, quantity_change: Decimal, reason: str, user: User) -> ProductStock:
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

    # Validar que el stock no quede negativo
    if (product_stock.quantity + quantity_change) < 0:
        raise ValidationError(f"Ajuste inválido. Stock resultante negativo para '{product_stock.product.name}'. Disponible: {product_stock.quantity}")

    # 1. Actualizar cantidad en la instancia
    product_stock.quantity += quantity_change

    # 2. Guardar Stock (BaseModel maneja modified_by/at)
    product_stock.save(user=user)

    # 3. Crear Evento
    StockEvent.objects.create(
        product_stock=product_stock,
        subproduct_stock=None,
        quantity_change=quantity_change,
        event_type='ingreso_ajuste' if quantity_change > 0 else 'egreso_ajuste',
        user=user,
        location=product_stock.location,
        notes=reason
    )
    print(f"--- Servicio: Stock ajustado para Producto {product_stock.product.pk} ---")
    return product_stock


# --- FUNCIONES PARA SUBPRODUCT STOCK ---

@transaction.atomic
def initialize_subproduct_stock(subproduct: Subproduct, user: User, initial_quantity: Decimal = Decimal('0.00'), location: str = None, reason: str = "Stock Inicial por Creación") -> SubproductStock:
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

    # Verificar si ya existe stock para este subproducto/ubicación
    query_params = {'subproduct': subproduct, 'location': location}
    existing_stock = SubproductStock.objects.filter(**query_params).first()
    if existing_stock:
        raise ValueError(f"Ya existe stock para '{subproduct.name}' en la ubicación '{location or 'N/A'}'. Use ajuste de stock.")

    # 1. Crear el registro SubproductStock
    stock_instance = SubproductStock(
        subproduct=subproduct,
        quantity=initial_quantity,
        location=location
    )
    stock_instance.save(user=user) # BaseModel asigna created_by

    # 2. Crear el evento de stock inicial (si cantidad > 0)
    if initial_quantity > 0:
        StockEvent.objects.create(
            product_stock=None,
            subproduct_stock=stock_instance, # FK a SubproductStock
            quantity_change=initial_quantity,
            event_type='ingreso_inicial',
            user=user,
            location=stock_instance.location,
            notes=reason
        )

    print(f"--- Servicio: Stock inicial creado para Subproducto {subproduct.pk} ---")
    return stock_instance

@transaction.atomic
def adjust_subproduct_stock(subproduct_stock: SubproductStock, quantity_change: Decimal, reason: str, user: User) -> SubproductStock:
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

    # Validar que el stock no quede negativo
    if (subproduct_stock.quantity + quantity_change) < 0:
        raise ValidationError(f"Ajuste inválido. Stock resultante negativo para '{subproduct_stock.subproduct.name}'. Disponible: {subproduct_stock.quantity}")

    # 1. Actualizar cantidad
    subproduct_stock.quantity += quantity_change

    # 2. Guardar Stock (BaseModel maneja modified_by/at)
    subproduct_stock.save(user=user)

    # 3. Crear Evento
    StockEvent.objects.create(
        product_stock=None,
        subproduct_stock=subproduct_stock,
        quantity_change=quantity_change,
        event_type='ingreso_ajuste' if quantity_change > 0 else 'egreso_ajuste',
        user=user,
        location=subproduct_stock.location,
        notes=reason
    )
    print(f"--- Servicio: Stock ajustado para Subproducto {subproduct_stock.subproduct.pk} ---")
    return subproduct_stock

@transaction.atomic
def dispatch_subproduct_stock_for_cut(subproduct: Subproduct, cutting_quantity: Decimal, order_pk: int, user_performing_cut: User, location: str = None) -> SubproductStock:
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

    # Obtener el registro de stock relevante (¡esta lógica puede ser más compleja!)
    # Asumimos por ahora que hay un único registro para el subproducto/ubicación.
    # Usamos select_for_update para bloquear la fila durante la transacción.
    try:
        stock_to_update = SubproductStock.objects.select_for_update().get(
            subproduct=subproduct,
            location=location,
            status=True
        )
    except SubproductStock.DoesNotExist:
        raise ValidationError(f"No se encontró stock activo para '{subproduct.name}' en la ubicación '{location or 'N/A'}'.")
    except SubproductStock.MultipleObjectsReturned:
         # ¡Manejar este caso! Quizás necesites lógica para elegir de qué lote/ubicación sacar
         raise ValidationError(f"Múltiples registros de stock encontrados para '{subproduct.name}' en la ubicación '{location or 'N/A'}'. Se requiere lógica adicional.")

    # Validar stock suficiente
    if cutting_quantity > stock_to_update.quantity:
        raise ValidationError(f"Stock insuficiente para corte de '{subproduct.name}'. Disponible: {stock_to_update.quantity}, Requerido: {cutting_quantity}")

    # 1. Actualizar cantidad
    stock_to_update.quantity -= cutting_quantity

    # 2. Guardar Stock (BaseModel maneja modified_by/at)
    stock_to_update.save(user=user_performing_cut)

    # 3. Crear Evento
    StockEvent.objects.create(
        product_stock=None,
        subproduct_stock=stock_to_update,
        quantity_change=-cutting_quantity, # Negativo para egreso
        event_type='egreso_corte',
        user=user_performing_cut,
        location=stock_to_update.location,
        notes=f"Egreso por Orden de Corte #{order_pk}"
    )
    print(f"--- Servicio: Stock descontado por corte para Subproducto {subproduct.pk} ---")
    return stock_to_update

# --- Puedes añadir más funciones aquí: ---
# - receive_initial_subproduct_stock(...)
# - dispatch_product_stock_for_sale(...)
# - transfer_stock(...)
