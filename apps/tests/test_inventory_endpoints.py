from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import User
from apps.tests.factories import create_category, create_type, create_product
from unittest.mock import patch

class InventoryEndpointsTestCase(TestCase):
    def setUp(self):
        self.patcher = patch("apps.products.utils.redis_utils.delete_keys_by_pattern", return_value=0)
        self.patcher.start()
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="pass",
            name="Admin",
            last_name="User",
        )
        self.client.force_authenticate(user=self.admin)

    def tearDown(self):
        self.patcher.stop()

    def test_category_crud(self):
        list_resp = self.client.get("/api/v1/inventory/categories/")
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)

        create_resp = self.client.post(
            "/api/v1/inventory/categories/create/",
            {"name": "CatTest", "status": True},
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        cat_id = create_resp.data["id"]

        detail_resp = self.client.get(f"/api/v1/inventory/categories/{cat_id}/")
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)

        update_resp = self.client.put(
            f"/api/v1/inventory/categories/{cat_id}/",
            {"name": "CatTestUpd"},
        )
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)

        delete_resp = self.client.delete(
            f"/api/v1/inventory/categories/{cat_id}/"
        )
        self.assertEqual(delete_resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_type_crud(self):
        category = create_category(user=self.admin)

        list_resp = self.client.get("/api/v1/inventory/types/")
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)

        create_resp = self.client.post(
            "/api/v1/inventory/types/create/",
            {"name": "TypeTest", "category": category.id, "status": True},
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        type_id = create_resp.data["id"]

        detail_resp = self.client.get(f"/api/v1/inventory/types/{type_id}/")
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)

        update_resp = self.client.put(
            f"/api/v1/inventory/types/{type_id}/",
            {"name": "TypeTestUpd"},
        )
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)

        delete_resp = self.client.delete(
            f"/api/v1/inventory/types/{type_id}/"
        )
        self.assertEqual(delete_resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_product_crud(self):
        category = create_category(user=self.admin)
        type_obj = create_type(category, user=self.admin)

        list_resp = self.client.get("/api/v1/inventory/products/")
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)

        create_resp = self.client.post(
            "/api/v1/inventory/products/create/",
            {
                "name": "ProdTest",
                "category": category.id,
                "type": type_obj.id,
                "status": True,
            },
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        prod_id = create_resp.data["id"]

        detail_resp = self.client.get(f"/api/v1/inventory/products/{prod_id}/")
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)

        update_resp = self.client.put(
            f"/api/v1/inventory/products/{prod_id}/",
            {"name": "ProdTestUpd"},
        )
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)

        delete_resp = self.client.delete(
            f"/api/v1/inventory/products/{prod_id}/"
        )
        self.assertEqual(delete_resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_subproduct_crud(self):
        category = create_category(user=self.admin)
        type_obj = create_type(category, user=self.admin)
        product = create_product(category, type_obj, user=self.admin)

        list_resp = self.client.get(
            f"/api/v1/inventory/products/{product.id}/subproducts/"
        )
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)

        create_resp = self.client.post(
            f"/api/v1/inventory/products/{product.id}/subproducts/create/",
            {"status": True, "number_coil": 1},
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        sub_id = create_resp.data["id"]

        detail_resp = self.client.get(
            f"/api/v1/inventory/products/{product.id}/subproducts/{sub_id}/"
        )
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)

        update_resp = self.client.put(
            f"/api/v1/inventory/products/{product.id}/subproducts/{sub_id}/",
            {"brand": "Updated"},
        )
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)

        delete_resp = self.client.delete(
            f"/api/v1/inventory/products/{product.id}/subproducts/{sub_id}/"
        )
        self.assertEqual(delete_resp.status_code, status.HTTP_204_NO_CONTENT)
