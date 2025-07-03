from django.test import TestCase

from apps.tests.factories import (
    create_user,
    create_category,
    create_type,
    create_product,
    create_product_stock,
)
from apps.stocks.api.repositories.stock_product_repository import StockProductRepository
from apps.stocks.models import ProductStock
from django.core.cache import cache


class StockProductRepositoryTestCase(TestCase):
    def setUp(self):
        cache.delete_pattern = lambda *args, **kwargs: None
        self.user = create_user(username='stock_user', email='stock@example.com')
        self.category = create_category(name='CatStock', user=self.user)
        self.type = create_type(self.category, name='TypeStock', user=self.user)
        self.product = create_product(self.category, self.type, user=self.user, name='ProdStock')

    def test_create_and_get_stock(self):
        stock = StockProductRepository.create_stock(self.product, 5, self.user)
        self.assertIsInstance(stock, ProductStock)
        fetched = StockProductRepository.get_stock_for_product(self.product)
        self.assertEqual(fetched.id, stock.id)
        self.assertEqual(fetched.quantity, stock.quantity)

    def test_soft_delete_stock(self):
        stock = create_product_stock(self.product, 3, user=self.user)
        StockProductRepository.soft_delete_stock(stock, user=self.user)
        self.assertFalse(stock.status)
        self.assertIsNone(StockProductRepository.get_by_stock_id(stock.id))

    def test_create_stock_negative_quantity(self):
        with self.assertRaises(ValueError):
            StockProductRepository.create_stock(self.product, -1, self.user)
