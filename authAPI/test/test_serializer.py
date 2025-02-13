from django.test import TestCase

from ..models import User
from ..serializer import UserSerializer

class UserSerializerTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'Testpassword123',
            'first_name': 'Test',
            'last_name': 'User',
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_serializer_serialization(self):
        """Prueba que el serializador serializa correctamente un usuario."""
        serializer = UserSerializer(self.user)
        expected_fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login'
        ]
        self.assertEqual(list(serializer.data.keys()), expected_fields)
        self.assertEqual(serializer.data['email'], self.user_data['email'])
        self.assertEqual(serializer.data['username'], self.user_data['username'])
        self.assertEqual(serializer.data['first_name'], self.user_data['first_name'])
        self.assertEqual(serializer.data['last_name'], self.user_data['last_name'])

    def test_user_serializer_deserialization(self):
        """Prueba que el serializador deserializa correctamente los datos para crear un usuario."""
        new_user_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'Newpassword123',
            'first_name': 'New',
            'last_name': 'User',
        }
        serializer = UserSerializer(data=new_user_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, new_user_data['email'])
        self.assertEqual(user.username, new_user_data['username'])
        self.assertEqual(user.first_name, new_user_data['first_name'])
        self.assertEqual(user.last_name, new_user_data['last_name'])

    def test_user_serializer_invalid_data(self):
        """Prueba que el serializador valida correctamente los datos inválidos."""
        invalid_user_data = {
            'email': 'invalidemail',
            'username': '',
            'password': 'short',
            'first_name': 'Test',
            'last_name': 'User',
        }
        serializer = UserSerializer(data=invalid_user_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('username', serializer.errors)
        self.assertIn('password', serializer.errors)

    def test_user_serializer_update(self):
        """Prueba que el serializador actualiza correctamente un usuario existente."""
        updated_data = {
            'first_name': 'Updated',
            'last_name': 'User',
        }
        serializer = UserSerializer(self.user, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.first_name, updated_data['first_name'])
        self.assertEqual(updated_user.last_name, updated_data['last_name'])