from django.test import TestCase

from django.urls import resolve, reverse

from ..views import UserViewSet

class URLTests(TestCase):
    def test_user_list_url_resolves(self):
        url = reverse('user-list')
        self.assertEqual(resolve(url).func.__name__, UserViewSet.as_view({'get': 'list'}).__name__)

    def test_user_login_url_resolves(self):
        url = reverse('user-login')
        self.assertEqual(resolve(url).func.__name__, UserViewSet.as_view({'post': 'login'}).__name__)