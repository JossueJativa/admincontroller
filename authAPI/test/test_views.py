from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from django.urls import reverse

from ..models import User

class UserViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='Testpassword123',
            first_name='Test',
            last_name='User'
        )

    def test_login(self):
        url = reverse('user-login')
        data = {'username': 'testuser', 'password': 'Testpassword123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn('access', response.data)

    def test_login_invalid_credentials(self):
        url = reverse('user-login')
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid credentials')