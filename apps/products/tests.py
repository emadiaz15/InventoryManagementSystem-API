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

from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from rest_framework import status
from apps.users.models import User
from apps.products.utils.cache_helpers import PRODUCT_LIST_CACHE_PREFIX
from apps.products.models.product_image_model import ProductImage


class ProductFileViewsTestCase(TestCase):
    def setUp(self):
        cache.delete_pattern = lambda *args, **kwargs: None
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="pass",
            name="Admin",
            last_name="User",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.category = create_category(name="Cat", user=self.admin)
        self.type = create_type(self.category, name="Type", user=self.admin)
        self.product = create_product(self.category, self.type, user=self.admin)

    @patch("apps.products.api.views.product_files_view.get_redis_connection")
    @patch("apps.products.api.views.product_files_view.upload_product_file")
    def test_upload_file_clears_cache(self, mock_upload, mock_get_redis):
        mock_upload.return_value = {
            "key": "k",
            "url": "http://example.com",
            "name": "f.pdf",
            "mimeType": "application/pdf",
        }
        redis_mock = MagicMock()
        mock_get_redis.return_value = redis_mock

        file = SimpleUploadedFile("f.pdf", b"data", content_type="application/pdf")
        url = f"/api/v1/inventory/products/{self.product.id}/files/upload/"
        response = self.client.post(url, {"file": file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        redis_mock.delete_pattern.assert_called_with(f"{PRODUCT_LIST_CACHE_PREFIX}*")

    @patch("apps.products.api.views.product_files_view.get_redis_connection")
    @patch("apps.products.api.views.product_files_view.delete_product_file")
    def test_delete_file_clears_cache(self, mock_delete_file, mock_get_redis):
        redis_mock = MagicMock()
        mock_get_redis.return_value = redis_mock

        image = ProductImage.objects.create(product=self.product, key="k2")
        url = f"/api/v1/inventory/products/{self.product.id}/files/{image.key}/delete/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        redis_mock.delete_pattern.assert_called_with(f"{PRODUCT_LIST_CACHE_PREFIX}*")


