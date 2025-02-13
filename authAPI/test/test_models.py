from django.test import TestCase

from ..models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='Testpassword123',
            first_name='Test',
            last_name='User'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('Testpassword123'))

    def test_user_str_method(self):
        self.assertEqual(str(self.user), 'testuser@example.com')

    def test_user_is_active_by_default(self):
        self.assertTrue(self.user.is_active)

    def test_user_is_not_staff_by_default(self):
        self.assertFalse(self.user.is_staff)

    def test_user_is_not_superuser_by_default(self):
        self.assertFalse(self.user.is_superuser)