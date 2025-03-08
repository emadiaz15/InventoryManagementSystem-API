from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from apps.cuts.models.cutting_order_model import CuttingOrder
from apps.products.models import Product
from apps.stocks.models.stock_model import Stock
from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class CuttingOrderAPITest(APITestCase):

    def setUp(self):
        """
        Configuración inicial para las pruebas de la API.
        Se crean un usuario, un producto y el stock relacionado.
        """
        self.supervisor = self._create_user(
            username="supervisor", 
            email="supervisor@example.com", 
            name="Supervisor", 
            last_name="User",
            dni="1234567890"
        )
        self.operator = self._create_user(
            username="operator", 
            email="operator@example.com", 
            name="Operator", 
            last_name="User",
            dni="0987654321"
        )
        
        # Crea el producto y el stock relacionado
        self.product = Product.objects.create(name="Cable")
        self.stock = Stock.objects.create(product=self.product, quantity=100, user=self.supervisor)

        # Generar el token JWT para autenticación
        refresh = RefreshToken.for_user(self.supervisor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def _create_user(self, username, email, name, last_name, dni, password="password123"):
        """
        Helper para crear un usuario con información básica.
        """
        return User.objects.create_user(
            username=username,
            password=password,
            email=email,
            name=name,
            last_name=last_name,
            dni=dni
        )

    def test_create_cutting_order(self):
        """
        Prueba para la creación de una orden de corte a través de la API.
        """
        url = reverse('cutting_orders')
        data = {
            "product": self.product.pk,
            "customer": "ACME Corp",
            "cutting_quantity": 50
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CuttingOrder.objects.count(), 1)
        self.assertEqual(CuttingOrder.objects.first().status, 'pending')

    def test_create_cutting_order_invalid_quantity(self):
        """
        Prueba para crear una orden con una cantidad mayor al stock disponible (debe fallar).
        """
        url = reverse('cutting_orders')
        data = {
            "product": self.product.pk,
            "customer": "ACME Corp",
            "cutting_quantity": 150  # Excede el stock
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_cutting_orders(self):
        """
        Prueba para listar las órdenes de corte a través de la API.
        """
        CuttingOrder.objects.create(
            product=self.product, customer="ACME Corp", cutting_quantity=30, assigned_by=self.supervisor
        )
        url = reverse('cutting_orders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

def test_update_cutting_order_status(self):
    """
    Prueba para actualizar el estado de una orden a 'in_process' y luego a 'completed' a través de la API.
    """
    # Crear una orden en estado 'pending'
    order = CuttingOrder.objects.create(
        product=self.product, customer="XYZ Corp", cutting_quantity=20, assigned_by=self.supervisor
    )
    url = reverse('cutting_order_detail', args=[order.pk])

    # Cambiar el estado a 'in_process'
    data = {"status": "in_process", "operator": self.operator.pk}
    response = self.client.patch(url, data, format='json')

    # Verificar que el estado ha cambiado correctamente a 'in_process'
    if response.status_code != status.HTTP_200_OK:
        print("Response content (in_process):", response.data)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # Refrescar la orden para verificar que está en estado 'in_process'
    order.refresh_from_db()
    self.assertEqual(order.status, "in_process")
    self.assertEqual(order.operator, self.operator)

    # Intentar completar la orden (estado 'completed')
    data = {"status": "completed"}
    response = self.client.patch(url, data, format='json')

    # Verificar si se ha podido completar la orden
    if response.status_code != status.HTTP_200_OK:
        print("Response content (completed):", response.data)
    
    # Validar que se ha completado correctamente
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    order.refresh_from_db()
    self.assertEqual(order.status, "completed")

    # Refrescar el stock del producto y verificar la actualización
    self.stock.refresh_from_db()
    self.assertEqual(self.stock.quantity, 80)  # El stock debe haberse actualizado correctamente
