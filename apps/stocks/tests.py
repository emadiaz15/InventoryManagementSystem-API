from django.test import TestCase
from apps.products.models import Product
from apps.stocks.models.stock_model import Stock
from django.contrib.auth import get_user_model

User = get_user_model()

class StockModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='user@test.com', password='pass', name='Test', last_name='User')
        self.product = Product.objects.create(name="Test Product", code=123)
        self.stock = Stock.objects.create(product=self.product, quantity=50, user=self.user)

    def test_stock_creation(self):
        self.assertEqual(self.stock.product, self.product)
        self.assertEqual(self.stock.quantity, 50)

    def test_stock_string_representation(self):
        self.assertEqual(str(self.stock), f'Stock for {self.product.name} on {self.stock.date}')
