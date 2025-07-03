from django.test import TestCase

from apps.tests.factories import create_user, create_category, create_type, create_product
from apps.products.api.repositories.product_repository import ProductRepository
from apps.products.models import Product
from django.core.cache import cache


class ProductRepositoryTestCase(TestCase):
    def setUp(self):
        cache.delete_pattern = lambda *args, **kwargs: None
        self.user = create_user(username='repo_user', email='repo@example.com')
        self.category = create_category(name='Cat1', user=self.user)
        self.type = create_type(self.category, name='Type1', user=self.user)

    def test_create_and_get_product(self):
        product = ProductRepository.create(
            name='Prod1',
            description='Desc',
            category_id=self.category.id,
            type_id=self.type.id,
            user=self.user,
        )
        self.assertIsInstance(product, Product)
        fetched = ProductRepository.get_by_id(product.id)
        self.assertEqual(fetched.id, product.id)
        self.assertEqual(fetched.name, 'Prod1')

    def test_soft_delete_product(self):
        product = create_product(self.category, self.type, user=self.user, name='Prod2')
        ProductRepository.soft_delete(product, user=self.user)
        self.assertFalse(product.status)
        self.assertIsNone(ProductRepository.get_by_id(product.id))
