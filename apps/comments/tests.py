from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from apps.comments.models.comment_subproduct_model import Comment
from apps.products.models import Product
from apps.users.models import User
from rest_framework.authtoken.models import Token

class CommentAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
            name='Test',
            last_name='User'
        )
        self.product = Product.objects.create(name='Test Product', code=12345)

        # Obtener el token JWT (si es necesario)
        # Por ejemplo, si estás usando JWT para autenticación
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_list_comments(self):
        url = reverse('comments-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_comment_api(self):
        url = reverse('comments-list')
        data = {
            'product': self.product.pk,
            'text': 'Great product!',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_comment(self):
        comment = Comment.objects.create(product=self.product, user=self.user, text='Good product.')
        url = reverse('comments-detail', args=[comment.pk])
        data = {
            'text': 'Updated comment',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_comment(self):
        comment = Comment.objects.create(product=self.product, user=self.user, text='Nice product.')
        url = reverse('comments-detail', args=[comment.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
