from django.test import TestCase
from django.urls import resolve, reverse
from ..views import DeskViewSet, AllergensViewSet, IngredientViewSet, DishViewSet, OrderViewSet, OrderDishViewSet

class URLTests(TestCase):
    def test_desk_list_url_resolves(self):
        url = reverse('desk-list')
        self.assertEqual(resolve(url).func.__name__, DeskViewSet.as_view({'get': 'list'}).__name__)

    def test_desk_detail_url_resolves(self):
        url = reverse('desk-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, DeskViewSet.as_view({'get': 'retrieve'}).__name__)

    def test_desk_create_url_resolves(self):
        url = reverse('desk-list')
        self.assertEqual(resolve(url).func.__name__, DeskViewSet.as_view({'post': 'create'}).__name__)

    def test_desk_update_url_resolves(self):
        url = reverse('desk-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, DeskViewSet.as_view({'put': 'update'}).__name__)

    def test_desk_delete_url_resolves(self):
        url = reverse('desk-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, DeskViewSet.as_view({'delete': 'destroy'}).__name__)

    def test_allergens_list_url_resolves(self):
        url = reverse('allergens-list')
        self.assertEqual(resolve(url).func.__name__, AllergensViewSet.as_view({'get': 'list'}).__name__)

    def test_allergens_detail_url_resolves(self):
        url = reverse('allergens-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, AllergensViewSet.as_view({'get': 'retrieve'}).__name__)

    def test_allergens_create_url_resolves(self):
        url = reverse('allergens-list')
        self.assertEqual(resolve(url).func.__name__, AllergensViewSet.as_view({'post': 'create'}).__name__)

    def test_allergens_update_url_resolves(self):
        url = reverse('allergens-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, AllergensViewSet.as_view({'put': 'update'}).__name__)

    def test_allergens_delete_url_resolves(self):
        url = reverse('allergens-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, AllergensViewSet.as_view({'delete': 'destroy'}).__name__)

    def test_ingredient_list_url_resolves(self):
        url = reverse('ingredient-list')
        self.assertEqual(resolve(url).func.__name__, IngredientViewSet.as_view({'get': 'list'}).__name__)

    def test_ingredient_detail_url_resolves(self):
        url = reverse('ingredient-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, IngredientViewSet.as_view({'get': 'retrieve'}).__name__)

    def test_ingredient_create_url_resolves(self):
        url = reverse('ingredient-list')
        self.assertEqual(resolve(url).func.__name__, IngredientViewSet.as_view({'post': 'create'}).__name__)

    def test_ingredient_update_url_resolves(self):
        url = reverse('ingredient-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, IngredientViewSet.as_view({'put': 'update'}).__name__)

    def test_ingredient_delete_url_resolves(self):
        url = reverse('ingredient-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, IngredientViewSet.as_view({'delete': 'destroy'}).__name__)

    def test_dish_list_url_resolves(self):
        url = reverse('dish-list')
        self.assertEqual(resolve(url).func.__name__, DishViewSet.as_view({'get': 'list'}).__name__)

    def test_dish_detail_url_resolves(self):
        url = reverse('dish-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, DishViewSet.as_view({'get': 'retrieve'}).__name__)

    def test_dish_create_url_resolves(self):
        url = reverse('dish-list')
        self.assertEqual(resolve(url).func.__name__, DishViewSet.as_view({'post': 'create'}).__name__)

    def test_dish_update_url_resolves(self):
        url = reverse('dish-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, DishViewSet.as_view({'put': 'update'}).__name__)

    def test_dish_delete_url_resolves(self):
        url = reverse('dish-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, DishViewSet.as_view({'delete': 'destroy'}).__name__)

    def test_order_list_url_resolves(self):
        url = reverse('order-list')
        self.assertEqual(resolve(url).func.__name__, OrderViewSet.as_view({'get': 'list'}).__name__)

    def test_order_detail_url_resolves(self):
        url = reverse('order-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, OrderViewSet.as_view({'get': 'retrieve'}).__name__)

    def test_order_create_url_resolves(self):
        url = reverse('order-list')
        self.assertEqual(resolve(url).func.__name__, OrderViewSet.as_view({'post': 'create'}).__name__)

    def test_order_update_url_resolves(self):
        url = reverse('order-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, OrderViewSet.as_view({'put': 'update'}).__name__)

    def test_order_delete_url_resolves(self):
        url = reverse('order-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, OrderViewSet.as_view({'delete': 'destroy'}).__name__)

    def test_orderdish_list_url_resolves(self):
        url = reverse('orderdish-list')
        self.assertEqual(resolve(url).func.__name__, OrderDishViewSet.as_view({'get': 'list'}).__name__)

    def test_orderdish_detail_url_resolves(self):
        url = reverse('orderdish-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, OrderDishViewSet.as_view({'get': 'retrieve'}).__name__)

    def test_orderdish_create_url_resolves(self):
        url = reverse('orderdish-list')
        self.assertEqual(resolve(url).func.__name__, OrderDishViewSet.as_view({'post': 'create'}).__name__)

    def test_orderdish_update_url_resolves(self):
        url = reverse('orderdish-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, OrderDishViewSet.as_view({'put': 'update'}).__name__)

    def test_orderdish_delete_url_resolves(self):
        url = reverse('orderdish-detail', args=[1])
        self.assertEqual(resolve(url).func.__name__, OrderDishViewSet.as_view({'delete': 'destroy'}).__name__)
