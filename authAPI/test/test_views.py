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
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        url = reverse('user-login')
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid credentials')

    def test_register(self):
        url = reverse('user-register')
        data = {'username': 'newuser', 'password': 'newpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_register_existing_username(self):
        url = reverse('user-register')
        data = {'username': 'testuser', 'password': 'newpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Username already exists')

    def test_logout(self):
        # First, log in to get the refresh token
        login_url = reverse('user-login')
        login_data = {'username': 'testuser', 'password': 'Testpassword123'}
        login_response = self.client.post(login_url, login_data, format='json')
        
        # Verify that the login was successful
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', login_response.data)
        
        # Now, log out using the refresh token
        logout_url = reverse('user-logout')
        logout_data = {'refresh': login_response.data['refresh']}
        response = self.client.post(logout_url, logout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'User logged out')

    def test_logout_invalid_token(self):
        url = reverse('user-logout')
        data = {'refresh': 'invalidtoken'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Token is invalid or expired')

    def test_logout_unset_token(self):
        url = reverse('user-logout')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Refresh token is required')