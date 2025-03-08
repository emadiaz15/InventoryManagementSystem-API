import os
from django.test import TestCase
from apps.products.models import Product, Category, Type
from django.contrib.auth import get_user_model
from apps.stocks.models.stock_model import Stock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

# Pruebas para el modelo Category
class CategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass',
            email='testuser@example.com',
            name='Test',
            last_name='User'
        )

    def test_create_category(self):
        category = Category.objects.create(
            name='Electronics',
            description='Category for electronic products',
            user=self.user
        )
        self.assertEqual(category.name, 'Electronics')
        self.assertEqual(category.description, 'Category for electronic products')
        self.assertEqual(category.user, self.user)


# Pruebas para el modelo Type
class TypeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass',
            email='testuser@example.com',
            name='Test',
            last_name='User'
        )

    def test_create_type(self):
        type_instance = Type.objects.create(
            name='Cable',
            description='Type for cables',
            user=self.user
        )
        self.assertEqual(type_instance.name, 'Cable')
        self.assertEqual(type_instance.description, 'Type for cables')
        self.assertEqual(type_instance.user, self.user)


# Pruebas para el modelo Product
class ProductModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass',
            email='testuser@example.com',
            name='Test',
            last_name='User'
        )
        self.category = Category.objects.create(
            name='Electronics',
            description='Category for electronic products',
            user=self.user
        )
        self.type = Type.objects.create(
            name='Cable',
            description='Type for cables',
            user=self.user
        )

    def test_create_product(self):
        product = Product.objects.create(
            name='Cable X',
            code=12345,
            type=self.type,
            category=self.category,
            brand='Brand A',
            user=self.user,
            metadata={'length': 50}
        )
        self.assertEqual(product.name, 'Cable X')
        self.assertEqual(product.code, 12345)
        self.assertEqual(product.type, self.type)
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.brand, 'Brand A')
        self.assertEqual(product.metadata['length'], 50)

    def test_add_wire_metadata(self):
        product = Product.objects.create(
            name='Cable Y',
            code=54321,
            type=self.type,
            category=self.category,
            brand='Brand B',
            user=self.user,
            metadata={'length': 100}
        )
        product.add_wire_metadata(number_coil='NC123', initial_length=100, total_weight=15.5)
        self.assertEqual(product.metadata['number_coil'], 'NC123')
        self.assertEqual(product.metadata['initial_length'], 100)
        self.assertEqual(product.metadata['total_weight'], 15.5)

    def test_generate_qr_code(self):
        product = Product.objects.create(
            name='Cable Z',
            code=67890,
            type=self.type,
            category=self.category,
            brand='Brand C',
            user=self.user,
            metadata={'length': 150}
        )
        
        # Llamar a la función para generar el QR code
        product.generate_qr_code()
        
        # Verificar que se ha generado un archivo de imagen
        self.assertIsNotNone(product.qr_code)  # Verifica que el campo qr_code no está vacío
        
        # Verifica que el archivo realmente se ha creado en el sistema de archivos
        qr_code_path = product.qr_code.path
        self.assertTrue(os.path.exists(qr_code_path))  # Asegúrate de que el archivo existe en la ruta


# Pruebas para el modelo Stock
class StockModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass',
            email='testuser@example.com',
            name='Test',
            last_name='User'
        )
        self.category = Category.objects.create(
            name='Electronics',
            description='Category for electronic products',
            user=self.user
        )
        self.type = Type.objects.create(
            name='Cable',
            description='Type for cables',
            user=self.user
        )
        self.product = Product.objects.create(
            name='Cable X',
            code=12345,
            type=self.type,
            category=self.category,
            brand='Brand A',
            user=self.user
        )

    def test_create_stock(self):
        stock = Stock.objects.create(
            product=self.product,
            quantity=100.0,
            user=self.user
        )
        self.assertEqual(stock.product, self.product)
        self.assertEqual(stock.quantity, 100.0)
        self.assertEqual(stock.user, self.user)

    def test_get_latest_stock(self):
        Stock.objects.create(product=self.product, quantity=100.0, user=self.user)
        Stock.objects.create(product=self.product, quantity=50.0, user=self.user)
        latest_stock = self.product.latest_stock
        self.assertEqual(latest_stock.quantity, 50.0)


# Pruebas para la API de generación y visualización del código QR
class ProductQRAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
            name='Test',
            last_name='User'
        )
        self.category = Category.objects.create(name="Electronics", user=self.user)
        self.type = Type.objects.create(name="Cable", user=self.user)
        self.product = Product.objects.create(
            name='Cable X',
            code=12345,
            type=self.type,
            category=self.category,
            brand='Brand A',
            user=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_generate_qr_code_view(self):
        url = reverse('generate_qr_code', args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('qr_code_url', response.data)

    def test_show_qr_code_image_view(self):
        self.product.generate_qr_code()
        url = reverse('show_qr_code_image', args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'image/png')
