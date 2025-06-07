from django.test import TestCase
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from decimal import Decimal
from rest_framework import status

from apps.products.models import Product, Subproduct
from apps.stocks.models import ProductStock, SubproductStock, StockEvent
User = get_user_model()

from apps.products.models import Category, Product, Type

class StockTestCase(TestCase):
    def setUp(self):
        # Crear las instancias de Category y Type si son necesarias
        self.category = Category.objects.create(name="Test Category")
        self.type = Type.objects.create(name="Test Type", category=self.category)
        
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

        # Crear el registro de stock asociado
        self.stock = ProductStock.objects.create(
            product=self.product,
            quantity=Decimal("100.00"),
            created_by=self.user
        )

    def test_get_product_stock_event_history(self):
        """Prueba la vista para obtener el historial de eventos de stock de un producto."""
        self.client.login(username="testuser", password="testpassword")

        # Crear un evento de stock
        stock_event = StockEvent.objects.create(
            product_stock=self.stock,
            quantity_change=Decimal("20.00"),
            event_type="ingreso",
            created_by=self.user,
            notes="Warehouse A",
        )

        # Realizar la solicitud GET
        response = self.client.get(f'/api/v1/stocks/products/{self.product.id}/stock/events/')

        # Verificar la respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['event_type'], 'ingreso')

    def test_get_subproduct_stock_event_history(self):
        """Prueba la vista para obtener el historial de eventos de stock de un subproducto."""
        # Supón que tienes un subproducto creado en tu base de datos
        subproduct = Subproduct.objects.create(brand="Subproduct 1", parent=self.product)
        subproduct_stock = SubproductStock.objects.create(
            quantity=Decimal("50.00"),
            subproduct=subproduct,
            created_by=self.user,
        )
        
        self.client.login(username="testuser", password="testpassword")
        
        # Crear un evento de stock
        stock_event = StockEvent.objects.create(
            subproduct_stock=subproduct_stock,
            quantity_change=Decimal("10.00"),
            event_type="ingreso",
            created_by=self.user,
            notes="Warehouse A",
        )

        # Realizar la solicitud GET
        response = self.client.get(f'/api/v1/stocks/products/{self.product.id}/subproducts/{subproduct.id}/stock/events/')

        # Verificar la respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['event_type'], 'ingreso')
