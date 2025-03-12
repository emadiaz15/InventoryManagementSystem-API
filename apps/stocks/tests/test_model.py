from django.test import TestCase
from apps.stocks.models.stock_event_model import ConcreteStock, StockEvent
from apps.products.models import Product
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.products.models import Category, Type, Product
User = get_user_model()

class StockTestCase(TestCase):

    def setUp(self):
        # Crear las instancias de Category y Type si son necesarias
        self.category = Category.objects.create(name="Test Category")
        self.type = Type.objects.create(name="Test Type")
        
        # Crear el usuario con todos los campos requeridos
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="testuser@example.com",  # Agregar el campo email
            name="Test",                   # Agregar el campo name
            last_name="User"               # Agregar el campo last_name
        )

        # Crear el producto con la categoría y el tipo
        self.product = Product.objects.create(
            name="Test Product",
            code=12345,
            description="Product for testing",
            status=True,
            category=self.category,  # Relacionado con la categoría
            type=self.type            # Relacionado con el tipo
        )
        """Prepara los datos necesarios para las pruebas."""
        self.product = Product.objects.create(name="Test Product", code=12345, description="Product for testing", status=True)
        self.stock = ConcreteStock.objects.create(name="Product Stock", quantity=Decimal(100.00), product=self.product, created_by=self.user)
    
    def test_create_stock_event(self):
        """Prueba la creación de un evento de stock (entrada)."""
        initial_quantity = self.stock.quantity
        stock_event = StockEvent.objects.create(
            stock_instance=self.stock,
            quantity_change=Decimal(20.00),
            user=self.user,
            location="Warehouse A"
        )
        # Verificar que el stock se actualizó correctamente
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, initial_quantity + Decimal(20.00))
        self.assertEqual(stock_event.event_type, 'entrada')
    
    def test_negative_stock(self):
        """Prueba para evitar un stock negativo."""
        with self.assertRaises(ValueError):
            StockEvent.objects.create(
                stock_instance=self.stock,
                quantity_change=Decimal(-200.00),  # Esto debería causar un error
                user=self.user,
                location="Warehouse A"
            )

    def test_delete_stock_event(self):
        """Prueba la eliminación del stock (soft delete)."""
        initial_quantity = self.stock.quantity
        self.stock.deleted_at = "2025-01-01"
        self.stock.save()
        self.assertIsNotNone(self.stock.deleted_at)
        self.assertEqual(self.stock.quantity, initial_quantity)  # La cantidad no debe cambiar tras el soft delete.
