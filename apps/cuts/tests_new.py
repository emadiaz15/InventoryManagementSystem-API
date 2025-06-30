from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.products.models import Category, Product, Subproduct
from apps.stocks.models import SubproductStock
from apps.cuts.models.cutting_order_model import CuttingOrder

User = get_user_model()

class CuttingOrderNewTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin', email='a@example.com', name='Admin', last_name='Ln', password='pass'
        )
        self.operator = User.objects.create_user(
            username='op', email='o@example.com', name='Op', last_name='Ln', password='pass'
        )
        self.category = Category.objects.create(name='Cat')
        self.product = Product.objects.create(name='Prod', category=self.category, has_subproducts=True)
        self.sub1 = Subproduct.objects.create(parent=self.product)
        self.sub2 = Subproduct.objects.create(parent=self.product)
        SubproductStock.objects.create(subproduct=self.sub1, quantity=50, created_by=self.admin)
        SubproductStock.objects.create(subproduct=self.sub2, quantity=50, created_by=self.admin)
        self.client.force_authenticate(user=self.admin)

    def test_create_order_multiple_items(self):
        url = reverse('cutting_order_create')
        payload = {
            'product': self.product.id,
            'customer': 'ACME',
            'order_number': 1,
            'items': [
                {'subproduct': self.sub1.id, 'cutting_quantity': 10},
                {'subproduct': self.sub2.id, 'cutting_quantity': 5}
            ]
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CuttingOrder.objects.count(), 1)
        order = CuttingOrder.objects.first()
        self.assertEqual(order.items.count(), 2)

    def test_operator_edit_items_flag(self):
        # Crear orden con flag False
        order = CuttingOrder.objects.create(product=self.product, customer='A', order_number=2,
                                            operator_can_edit_items=False, created_by=self.admin,
                                            assigned_to=self.operator)
        url = reverse('cutting_order_detail', args=[order.id])
        self.client.force_authenticate(user=self.operator)
        payload = {'items': [{'subproduct': self.sub1.id, 'cutting_quantity': 1}]}
        resp = self.client.patch(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        # Ahora con flag True
        order.operator_can_edit_items = True
        order.save(user=self.admin)
        resp = self.client.patch(url, payload, format='json')
        self.assertNotEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

