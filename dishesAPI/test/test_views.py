from django.test import TestCase

from datetime import time

from rest_framework.test import APIClient
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from authAPI.models import User
from ..models import Desk, Allergens, Ingredient, Dish, Order, OrderDish
from ..serializer import DeskSerializer, AllergensSerializer, IngredientSerializer, DishSerializer, OrderSerializer, OrderDishSerializer

class BaseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

class DeskViewSetTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.desk = Desk.objects.create(desk_number=1, capacity=4)

    def test_get_desk(self):
        response = self.client.get(f'/api/desk/{self.desk.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, DeskSerializer(self.desk).data)

    def test_create_desk(self):
        response = self.client.post('/api/desk/', {'desk_number': 2, 'capacity': 4})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_desk_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.post('/api/desk/', {'desk_number': 2, 'capacity': 4})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_desk(self):
        response = self.client.put(f'/api/desk/{self.desk.id}/', {'desk_number': 3, 'capacity': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.desk.refresh_from_db()
        self.assertEqual(self.desk.desk_number, 3)
        self.assertEqual(self.desk.capacity, 5)

    def test_update_desk_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.put(f'/api/desk/{self.desk.id}/', {'desk_number': 3, 'capacity': 5})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_desk(self):
        response = self.client.delete(f'/api/desk/{self.desk.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Desk.objects.filter(id=self.desk.id).exists())

    def test_delete_desk_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.delete(f'/api/desk/{self.desk.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AllergensViewSetTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.allergen = Allergens.objects.create(allergen_name="Peanuts")

    def test_get_allergen(self):
        response = self.client.get(f'/api/allergens/{self.allergen.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, AllergensSerializer(self.allergen).data)

    def test_create_allergen(self):
        self.client.force_authenticate(user=self.user)  # Ensure the user is authenticated
        response = self.client.post('/api/allergens/', {'allergen_name': 'Gluten'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_allergen_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.post('/api/allergens/', {'allergen_name': 'Gluten'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_allergen(self):
        response = self.client.put(f'/api/allergens/{self.allergen.id}/', {'allergen_name': 'Soy'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.allergen.refresh_from_db()
        self.assertEqual(self.allergen.allergen_name, 'Soy')

    def test_update_allergen_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.put(f'/api/allergens/{self.allergen.id}/', {'allergen_name': 'Soy'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_allergen(self):
        response = self.client.delete(f'/api/allergens/{self.allergen.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Allergens.objects.filter(id=self.allergen.id).exists())

    def test_delete_allergen_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.delete(f'/api/allergens/{self.allergen.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class IngredientViewSetTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.allergen = Allergens.objects.create(allergen_name="Peanuts")
        self.ingredient = Ingredient.objects.create(ingredient_name="Flour", quantity=2)
        self.ingredient.allergen.add(self.allergen)

    def test_get_ingredient(self):
        response = self.client.get(f'/api/ingredient/{self.ingredient.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, IngredientSerializer(self.ingredient).data)

    def test_create_ingredient(self):
        response = self.client.post('/api/ingredient/', {'ingredient_name': 'Sugar', 'quantity': 5, 'allergen': [self.allergen.id]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ingredient_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.post('/api/ingredient/', {'ingredient_name': 'Sugar', 'quantity': 5, 'allergen': [self.allergen.id]})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_ingredient(self):
        response = self.client.put(f'/api/ingredient/{self.ingredient.id}/', {'ingredient_name': 'Salt', 'quantity': 3, 'allergen': [self.allergen.id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ingredient.refresh_from_db()
        self.assertEqual(self.ingredient.ingredient_name, 'Salt')
        self.assertEqual(self.ingredient.quantity, 3)

    def test_update_ingredient_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.put(f'/api/ingredient/{self.ingredient.id}/', {'ingredient_name': 'Salt', 'quantity': 3, 'allergen': [self.allergen.id]})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_ingredient(self):
        response = self.client.delete(f'/api/ingredient/{self.ingredient.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=self.ingredient.id).exists())

    def test_delete_ingredient_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.delete(f'/api/ingredient/{self.ingredient.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class DishViewSetTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.ingredient = Ingredient.objects.create(ingredient_name="Flour", quantity=2)
        self.dish = Dish.objects.create(dish_name="Pizza", description="Delicious pizza", time_elaboration="00:30:00", price=10, link_ar="http://example.com")
        self.dish.ingredient.add(self.ingredient)

    def test_get_dish(self):
        response = self.client.get(f'/api/dish/{self.dish.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, DishSerializer(self.dish).data)

    def test_create_dish(self):
        response = self.client.post('/api/dish/', {'dish_name': 'Burger', 'description': 'Tasty burger', 'time_elaboration': '00:20:00', 'price': 8, 'link_ar': 'http://example.com', 'ingredient': [self.ingredient.id]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_dish_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.post('/api/dish/', {'dish_name': 'Burger', 'description': 'Tasty burger', 'time_elaboration': '00:20:00', 'price': 8, 'link_ar': 'http://example.com', 'ingredient': [self.ingredient.id]})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_dish(self):
        response = self.client.put(f'/api/dish/{self.dish.id}/', {
            'dish_name': 'Pasta', 
            'description': 'Delicious pasta', 
            'time_elaboration': '00:25:00', 
            'price': 12, 
            'link_ar': 'http://example.com', 
            'ingredient': [self.ingredient.id]
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dish.refresh_from_db()
        self.assertEqual(self.dish.dish_name, 'Pasta')
        self.assertEqual(self.dish.description, 'Delicious pasta')
        self.assertEqual(self.dish.time_elaboration, time(0, 25))
        self.assertEqual(self.dish.price, 12)
        self.assertIn(self.ingredient, self.dish.ingredient.all())

    def test_update_dish_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.put(f'/api/dish/{self.dish.id}/', {
            'dish_name': 'Pasta', 
            'description': 'Delicious pasta', 
            'time_elaboration': '00:25:00', 
            'price': 12, 
            'link_ar': 'http://example.com', 
            'ingredient': [self.ingredient.id]
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_dish(self):
        response = self.client.delete(f'/api/dish/{self.dish.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Dish.objects.filter(id=self.dish.id).exists())

    def test_delete_dish_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.delete(f'/api/dish/{self.dish.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class OrderViewSetTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.desk = Desk.objects.create(desk_number=1, capacity=4)
        self.dish = Dish.objects.create(dish_name="Pizza", description="Delicious pizza", time_elaboration="00:30:00", price=10, link_ar="http://example.com")
        self.order = Order.objects.create(desk=self.desk, date='2023-10-01', time='12:00:00', total_price=100, status='Pending')
        self.order_dish = OrderDish.objects.create(order=self.order, dish=self.dish, quantity=2)  # Crear OrderDish

    def test_get_order(self):
        response = self.client.get(f'/api/order/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrderSerializer(self.order).data)

    def test_create_order(self):
        response = self.client.post('/api/order/', {'desk': self.desk.id, 'date': '2023-10-02', 'time': '13:00:00', 'total_price': 150, 'status': 'Confirmed'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_order(self):
        response = self.client.put(f'/api/order/{self.order.id}/', {'desk': self.desk.id, 'date': '2023-10-03', 'time': '14:00:00', 'total_price': 200, 'status': 'Completed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.date.strftime('%Y-%m-%d'), '2023-10-03')  # Convertir a string para comparación
        self.assertEqual(self.order.time, time(14, 0))
        self.assertEqual(self.order.total_price, 200)
        self.assertEqual(self.order.status, 'Completed')

    def test_delete_order(self):
        response = self.client.delete(f'/api/order/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

class OrderDishViewSetTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.desk = Desk.objects.create(desk_number=1, capacity=4)
        self.order = Order.objects.create(desk=self.desk, date='2023-10-01', time='12:00:00', total_price=100, status='Pending')
        self.dish = Dish.objects.create(dish_name="Pizza", description="Delicious pizza", time_elaboration="00:30:00", price=10, link_ar="http://example.com")
        self.order_dish = OrderDish.objects.create(order=self.order, dish=self.dish, quantity=2)

    def test_get_order_dish(self):
        response = self.client.get(f'/api/orderdish/{self.order_dish.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrderDishSerializer(self.order_dish).data)

    def test_create_order_dish(self):
        response = self.client.post('/api/orderdish/', {'order': self.order.id, 'dish': self.dish.id, 'quantity': 3})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_order_dish(self):
        response = self.client.put(f'/api/orderdish/{self.order_dish.id}/', {'order': self.order.id, 'dish': self.dish.id, 'quantity': 4})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order_dish.refresh_from_db()
        self.assertEqual(self.order_dish.quantity, 4)

    def test_delete_order_dish(self):
        response = self.client.delete(f'/api/orderdish/{self.order_dish.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(OrderDish.objects.filter(id=self.order_dish.id).exists())