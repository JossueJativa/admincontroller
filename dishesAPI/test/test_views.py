from django.test import TestCase
from datetime import time, timedelta, datetime
from rest_framework.test import APIClient
from rest_framework import status
import jwt
from django.conf import settings
from authAPI.models import User
from ..models import Desk, Allergens, Ingredient, Dish, Order, OrderDish, Category, Garrison, Invoice, InvoiceDish
from ..serializer import DeskSerializer, AllergensSerializer, IngredientSerializer, DishSerializer, OrderSerializer, OrderDishSerializer, CategorySerializer
from dishesAPI import views
import os

class BaseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # Manual JWT generation (matches backend logic)
        payload = {
            'user_id': self.user.id,
            'exp': datetime.utcnow() + timedelta(minutes=60),
            'iat': datetime.utcnow(),
            'type': 'access'  # Asegura que el token es de tipo access
        }
        secret = getattr(settings, 'SECRET_KEY', 'test-secret')
        token = jwt.encode(payload, secret, algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

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
        self.ingredient = Ingredient.objects.create(ingredient_name="Flour")
        self.ingredient.allergen.add(self.allergen)

    def test_get_ingredient(self):
        response = self.client.get(f'/api/ingredient/{self.ingredient.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, IngredientSerializer(self.ingredient).data)

    def test_create_ingredient(self):
        response = self.client.post('/api/ingredient/', {'ingredient_name': 'Sugar', 'allergen': [self.allergen.id]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_ingredient_without_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION='')  # Remove authentication header
        response = self.client.post('/api/ingredient/', {'ingredient_name': 'Sugar', 'allergen': [self.allergen.id]})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_ingredient(self):
        response = self.client.put(f'/api/ingredient/{self.ingredient.id}/', {'ingredient_name': 'Sugar', 'allergen': [self.allergen.id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ingredient.refresh_from_db()
        self.assertEqual(self.ingredient.ingredient_name, 'Sugar')

    def test_update_ingredient_without_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION='')  # Remove authentication header
        response = self.client.put(f'/api/ingredient/{self.ingredient.id}/', {'ingredient_name': 'Salt', 'allergen': [self.allergen.id]})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_ingredient(self):
        response = self.client.delete(f'/api/ingredient/{self.ingredient.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=self.ingredient.id).exists())

    def test_delete_ingredient_without_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION='')  # Remove authentication header
        response = self.client.delete(f'/api/ingredient/{self.ingredient.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class DishViewSetTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(category_name="Appetizers")
        self.ingredient = Ingredient.objects.create(ingredient_name="Flour")
        self.dish = Dish.objects.create(
            dish_name="Pizza",
            description="Delicious pizza",
            time_elaboration="00:30:00",
            price=10,
            link_ar="http://example.com",
            category=self.category,
            has_garrison=True  # Dish with garrison
        )
        self.dish.ingredient.add(self.ingredient)

    def test_get_dish(self):
        response = self.client.get(f'/api/dish/{self.dish.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, DishSerializer(self.dish).data)

    def test_create_dish(self):
        response = self.client.post('/api/dish/', {'dish_name': 'Burger', 'description': 'Tasty burger', 'time_elaboration': '00:20:00', 'price': 8, 'link_ar': 'http://example.com', 'ingredient': [self.ingredient.id], 'category': self.category.id, 'has_garrison': False})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_dish_with_garrison(self):
        response = self.client.post('/api/dish/', {
            'dish_name': 'Burger',
            'description': 'Tasty burger',
            'time_elaboration': '00:20:00',
            'price': 8,
            'link_ar': 'http://example.com',
            'ingredient': [self.ingredient.id],
            'category': self.category.id,
            'has_garrison': True
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['has_garrison'])

    def test_create_dish_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.post('/api/dish/', {'dish_name': 'Burger', 'description': 'Tasty burger', 'time_elaboration': '00:20:00', 'price': 8, 'link_ar': 'http://example.com', 'ingredient': [self.ingredient.id], 'category': self.category.id, 'has_garrison': False})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_dish(self):
        response = self.client.put(f'/api/dish/{self.dish.id}/', {
            'dish_name': 'Pasta', 
            'description': 'Delicious pasta', 
            'time_elaboration': '00:25:00', 
            'price': 12, 
            'link_ar': 'http://example.com', 
            'ingredient': [self.ingredient.id],
            'category': self.category.id,
            'has_garrison': False
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
            'ingredient': [self.ingredient.id],
            'category': self.category.id,
            'has_garrison': False
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
        self.category = Category.objects.create(category_name="Appetizers")  # Add category
        self.desk = Desk.objects.create(desk_number=1, capacity=4)
        self.dish = Dish.objects.create(
            dish_name="Pizza", 
            description="Delicious pizza", 
            time_elaboration="00:30:00", 
            price=10, 
            link_ar="http://example.com",
            category=self.category  # Assign category
        )
        self.order = Order.objects.create(
            desk=self.desk, 
            date='2023-10-01', 
            time='12:00:00', 
            total_price=100, 
            status='Pending'
        )
        self.order_dish = OrderDish.objects.create(order=self.order, dish=self.dish, quantity=2)

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
        self.category = Category.objects.create(category_name="Appetizers")  # Add category
        self.desk = Desk.objects.create(desk_number=1, capacity=4)
        self.order = Order.objects.create(
            desk=self.desk, 
            date='2023-10-01', 
            time='12:00:00', 
            total_price=100, 
            status='Pending'
        )
        self.dish = Dish.objects.create(
            dish_name="Pizza", 
            description="Delicious pizza", 
            time_elaboration="00:30:00", 
            price=10, 
            link_ar="http://example.com",
            category=self.category  # Assign category
        )
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

class CategoryViewSetTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(category_name="Appetizers")

    def test_get_category(self):
        response = self.client.get(f'/api/category/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, CategorySerializer(self.category).data)

    def test_create_category(self):
        response = self.client.post('/api/category/', {'category_name': 'Main Course'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.post('/api/category/', {'category_name': 'Main Course'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_category(self):
        response = self.client.put(f'/api/category/{self.category.id}/', {'category_name': 'Desserts'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.category_name, 'Desserts')

    def test_update_category_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.put(f'/api/category/{self.category.id}/', {'category_name': 'Desserts'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_category(self):
        response = self.client.delete(f'/api/category/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def test_delete_category_without_auth(self):
        self.client.credentials()  # Remove authentication
        response = self.client.delete(f'/api/category/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class GarrisonViewSetTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(category_name="Appetizers")
        self.dish = Dish.objects.create(
            dish_name="Pizza",
            description="Delicious pizza",
            time_elaboration="00:30:00",
            price=10,
            link_ar="http://example.com",
            category=self.category,
            has_garrison=True
        )
        self.garrison = Garrison.objects.create(garrison_name="Fries")
        self.garrison.dish.add(self.dish)

    def test_get_garrison(self):
        response = self.client.get(f'/api/garrison/{self.garrison.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['garrison_name'], "Fries")

    def test_create_garrison(self):
        response = self.client.post('/api/garrison/', {
            'garrison_name': 'Salad',
            'dish': [self.dish.id]
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['garrison_name'], 'Salad')

    def test_update_garrison(self):
        response = self.client.put(f'/api/garrison/{self.garrison.id}/', {
            'garrison_name': 'Mashed Potatoes',
            'dish': [self.dish.id]
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.garrison.refresh_from_db()
        self.assertEqual(self.garrison.garrison_name, 'Mashed Potatoes')

    def test_delete_garrison(self):
        response = self.client.delete(f'/api/garrison/{self.garrison.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Garrison.objects.filter(id=self.garrison.id).exists())

class InvoiceViewSetTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.desk = Desk.objects.create(desk_number=1, capacity=4)
        self.category = Category.objects.create(category_name="Appetizers")
        self.dish = Dish.objects.create(
            dish_name="Pizza",
            description="Delicious pizza",
            time_elaboration="00:30:00",
            price=10,
            link_ar="http://example.com",
            category=self.category
        )
        self.order = Order.objects.create(
            desk=self.desk,
            date="2023-10-10",
            time="12:00:00",
            total_price=10,
            status="Pending"
        )
        self.invoice = Invoice.objects.create(
            order=self.order,
            invoice_number="INV123",
            total_price=10
        )

    def test_get_invoice(self):
        response = self.client.get(f'/api/invoice/{self.invoice.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['invoice_number'], "INV123")

    def test_create_invoice(self):
        response = self.client.post('/api/invoice/', {
            'order': self.order.id,
            'invoice_number': 'INV124',
            'total_price': 20
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_invoice(self):
        response = self.client.put(f'/api/invoice/{self.invoice.id}/', {
            'order': self.order.id,
            'invoice_number': 'INV125',
            'total_price': 30
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.invoice_number, 'INV125')
        self.assertEqual(self.invoice.total_price, 30)

    def test_delete_invoice(self):
        response = self.client.delete(f'/api/invoice/{self.invoice.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Invoice.objects.filter(id=self.invoice.id).exists())

class InvoiceDishViewSetTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.desk = Desk.objects.create(desk_number=1, capacity=4)
        self.category = Category.objects.create(category_name="Appetizers")
        self.dish = Dish.objects.create(
            dish_name="Pizza",
            description="Delicious pizza",
            time_elaboration="00:30:00",
            price=10,
            link_ar="http://example.com",
            category=self.category
        )
        self.order = Order.objects.create(
            desk=self.desk,
            date="2023-10-10",
            time="12:00:00",
            total_price=10,
            status="Pending"
        )
        self.invoice = Invoice.objects.create(
            order=self.order,
            invoice_number="INV123",
            total_price=10
        )
        self.invoice_dish = InvoiceDish.objects.create(
            invoice=self.invoice,
            dish=self.dish,
            quantity=2
        )

    def test_get_invoice_dish(self):
        response = self.client.get(f'/api/invoicedish/{self.invoice_dish.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 2)

    def test_create_invoice_dish(self):
        response = self.client.post('/api/invoicedish/', {
            'invoice': self.invoice.id,
            'dish': self.dish.id,
            'quantity': 3
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_invoice_dish(self):
        response = self.client.put(f'/api/invoicedish/{self.invoice_dish.id}/', {
            'invoice': self.invoice.id,
            'dish': self.dish.id,
            'quantity': 4
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.invoice_dish.refresh_from_db()
        self.assertEqual(self.invoice_dish.quantity, 4)

    def test_delete_invoice_dish(self):
        response = self.client.delete(f'/api/invoicedish/{self.invoice_dish.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(InvoiceDish.objects.filter(id=self.invoice_dish.id).exists())

class UnifiedStatisticsTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(category_name="Entradas")
        self.desk = Desk.objects.create(desk_number=1, capacity=4)
        self.dish = Dish.objects.create(
            dish_name="Sopa de Tortilla",
            description="Deliciosa sopa mexicana",
            time_elaboration="00:30:00",
            price=6.99,
            category=self.category,
            has_garrison=False
        )
        self.order = Order.objects.create(
            desk=self.desk,
            date="2025-05-01",
            time="12:00:00",
            total_price=6.99,
            status="Completo"
        )
        self.order_dish = OrderDish.objects.create(order=self.order, dish=self.dish, quantity=1)

    def test_unified_statistics(self):
        response = self.client.get('/api/order/unified_statistics/?year=2025&month=5')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('dashboard_statistics', response.data)

        dashboard_statistics = response.data['dashboard_statistics']
        self.assertEqual(dashboard_statistics['total_dishes'], 1)
        self.assertEqual(dashboard_statistics['total_revenue'], 6.99)
        self.assertEqual(dashboard_statistics['average_dishes_per_table'], 1.0)

        self.assertEqual(len(dashboard_statistics['dishes']), 1)
        self.assertEqual(dashboard_statistics['dishes'][0]['dish__dish_name'], "Sopa de Tortilla")
        self.assertEqual(dashboard_statistics['dishes'][0]['count'], 1)

        self.assertEqual(len(dashboard_statistics['categories']), 1)
        self.assertEqual(dashboard_statistics['categories'][0]['dish__category__category_name'], "Entradas")
        self.assertEqual(dashboard_statistics['categories'][0]['count'], 1)

class TranslateFieldsTestCase(TestCase):
    def test_translate_fields_success(self):
        data = [{'name': 'Hola'}]
        fields = ['name']
        target_lang = 'EN-GB'

        class FakeTranslation:
            def __init__(self, text):
                self.text = text
        class FakeTranslator:
            def __init__(self, key):
                pass
            def translate_text(self, texts, target_lang=None):
                return [FakeTranslation('Hello') for _ in texts]

        with self.settings(DEEPL_AUTH_KEY='fake-key'):
            os.environ['DEEPL_AUTH_KEY'] = 'fake-key'
            original_translator = views.deepl.Translator
            views.deepl.Translator = FakeTranslator
            try:
                views.translate_fields(data, fields, target_lang)
            finally:
                views.deepl.Translator = original_translator
        self.assertEqual(data[0]['name'], 'Hello')

    def test_translate_fields_no_api_key(self):
        data = [{'name': 'Hola'}]
        fields = ['name']
        target_lang = 'EN-GB'
        if 'DEEPL_AUTH_KEY' in os.environ:
            del os.environ['DEEPL_AUTH_KEY']
        with self.assertRaises(ValueError) as exc:
            views.translate_fields(data, fields, target_lang)
        self.assertIn('DeepL API key is not configured', str(exc.exception))

    def test_translate_fields_deepl_exception(self):
        data = [{'name': 'Hola'}]
        fields = ['name']
        target_lang = 'EN-GB'
        class FakeTranslator:
            def __init__(self, key):
                pass
            def translate_text(self, texts, target_lang=None):
                raise views.deepl.exceptions.DeepLException('DeepL error')
        with self.settings(DEEPL_AUTH_KEY='fake-key'):
            os.environ['DEEPL_AUTH_KEY'] = 'fake-key'
            original_translator = views.deepl.Translator
            views.deepl.Translator = FakeTranslator
            try:
                with self.assertRaises(views.deepl.exceptions.DeepLException):
                    views.translate_fields(data, fields, target_lang)
            finally:
                views.deepl.Translator = original_translator

    def test_translate_fields_generic_exception(self):
        data = [{'name': 'Hola'}]
        fields = ['name']
        target_lang = 'EN-GB'
        class FakeTranslator:
            def __init__(self, key):
                pass
            def translate_text(self, texts, target_lang=None):
                raise Exception('Generic error')
        with self.settings(DEEPL_AUTH_KEY='fake-key'):
            os.environ['DEEPL_AUTH_KEY'] = 'fake-key'
            original_translator = views.deepl.Translator
            views.deepl.Translator = FakeTranslator
            try:
                with self.assertRaises(Exception) as exc:
                    views.translate_fields(data, fields, target_lang)
                self.assertIn('Generic error', str(exc.exception))
            finally:
                views.deepl.Translator = original_translator

class TranslateResponseTestCase(TestCase):
    def test_translate_response_unsupported_language(self):
        class DummyRequest:
            query_params = {'lang': 'FR'}
        data = [{'category_name': 'Hola'}]
        view = views.CategoryViewSet()
        with self.assertRaises(ValueError) as exc:
            view.translate_response(data, ['category_name'], DummyRequest())
        self.assertIn('not supported', str(exc.exception))

    def test_translate_response_no_translation(self):
        class DummyRequest:
            query_params = {'lang': 'ES'}
        data = [{'category_name': 'Hola'}]
        view = views.CategoryViewSet()
        # Patch translate_fields to fail if called
        original_translate_fields = views.translate_fields
        views.translate_fields = lambda *a, **k: (_ for _ in ()).throw(Exception('Should not be called'))
        try:
            view.translate_response(data, ['category_name'], DummyRequest())
        finally:
            views.translate_fields = original_translate_fields
        self.assertEqual(data[0]['category_name'], 'Hola')

class CategoryViewSetListErrorTestCase(TestCase):
    def setUp(self):
        self.view = views.CategoryViewSet()
        self.factory = APIClient()
        self.user = User.objects.create_user(username='testuser2', password='testpass')
        self.request = self.factory.get('/api/category/?lang=FR')
        self.request.user = self.user

    def test_list_value_error(self):
        # Forzar ValueError en translate_response
        original_translate_response = self.view.translate_response
        def fake_translate_response(*a, **k):
            raise ValueError('Language not supported')
        self.view.translate_response = fake_translate_response
        self.view.request = self.request  # Fix: asignar self.request
        self.view.format_kwarg = None  # Fix: asignar format_kwarg
        response = self.view.list(self.request)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Language not supported', str(response.data))
        self.view.translate_response = original_translate_response

    def test_list_generic_exception(self):
        original_translate_response = self.view.translate_response
        def fake_translate_response(*a, **k):
            raise Exception('Unexpected error')
        self.view.translate_response = fake_translate_response
        self.view.request = self.request  # Fix: asignar self.request
        self.view.format_kwarg = None  # Fix: asignar format_kwarg
        response = self.view.list(self.request)
        self.assertEqual(response.status_code, 500)
        self.assertIn('unexpected', str(response.data['error']).lower())
        self.view.translate_response = original_translate_response

class DishViewSetListRetrieveErrorTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(category_name="Appetizers")
        self.ingredient = Ingredient.objects.create(ingredient_name="Flour")
        self.dish = Dish.objects.create(
            dish_name="Pizza",
            description="Delicious pizza",
            time_elaboration="00:30:00",
            price=10,
            link_ar="http://example.com",
            category=self.category,
            has_garrison=True
        )
        self.dish.ingredient.add(self.ingredient)
        self.view = views.DishViewSet()
        self.factory = APIClient()
        self.user = User.objects.create_user(username='testuser3', password='testpass')
        self.request = self.factory.get('/api/dish/?lang=EN')
        self.request.user = self.user

    def test_list_value_error(self):
        original_translate_response = self.view.translate_response
        def fake_translate_response(*a, **k):
            raise ValueError('Language not supported')
        self.view.translate_response = fake_translate_response
        self.view.request = self.request  # Fix: asignar self.request
        self.view.format_kwarg = None  # Fix: asignar format_kwarg
        response = self.view.list(self.request)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Language not supported', str(response.data))
        self.view.translate_response = original_translate_response

    def test_list_generic_exception(self):
        original_translate_response = self.view.translate_response
        def fake_translate_response(*a, **k):
            raise Exception('Unexpected error')
        self.view.translate_response = fake_translate_response
        self.view.request = self.request  # Fix: asignar self.request
        self.view.format_kwarg = None  # Fix: asignar format_kwarg
        response = self.view.list(self.request)
        self.assertEqual(response.status_code, 500)
        self.assertIn('unexpected', str(response.data['error']).lower())
        self.view.translate_response = original_translate_response

    def test_retrieve_value_error(self):
        original_translate_response = self.view.translate_response
        def fake_translate_response(*a, **k):
            raise ValueError('Language not supported')
        self.view.translate_response = fake_translate_response
        # Simular get_object y get_serializer
        self.view.get_object = lambda: self.dish
        self.view.get_serializer = lambda instance: DishSerializer(instance)
        request = self.factory.get(f'/api/dish/{self.dish.id}/?lang=FR')
        request.user = self.user
        response = self.view.retrieve(request, pk=self.dish.id)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Language not supported', str(response.data))
        self.view.translate_response = original_translate_response

    def test_retrieve_generic_exception(self):
        original_translate_response = self.view.translate_response
        def fake_translate_response(*a, **k):
            raise Exception('Unexpected error')
        self.view.translate_response = fake_translate_response
        self.view.get_object = lambda: self.dish
        self.view.get_serializer = lambda instance: DishSerializer(instance)
        request = self.factory.get(f'/api/dish/{self.dish.id}/?lang=FR')
        request.user = self.user
        response = self.view.retrieve(request, pk=self.dish.id)
        self.assertEqual(response.status_code, 500)
        self.assertIn('unexpected', str(response.data['error']).lower())
        self.view.translate_response = original_translate_response

class GarrisonViewSetListErrorTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(category_name="Appetizers")
        self.dish = Dish.objects.create(
            dish_name="Pizza",
            description="Delicious pizza",
            time_elaboration="00:30:00",
            price=10,
            link_ar="http://example.com",
            category=self.category,
            has_garrison=True
        )
        self.garrison = Garrison.objects.create(garrison_name="Fries")
        self.garrison.dish.add(self.dish)
        self.view = views.GarrisonViewSet()
        self.factory = APIClient()
        self.user = User.objects.create_user(username='testuser4', password='testpass')
        self.request = self.factory.get('/api/garrison/?lang=FR')
        self.request.user = self.user

    def test_list_value_error(self):
        original_translate_response = self.view.translate_response
        def fake_translate_response(*a, **k):
            raise ValueError('Language not supported')
        self.view.translate_response = fake_translate_response
        self.view.request = self.request  # Fix: asignar self.request
        self.view.format_kwarg = None  # Fix: asignar format_kwarg
        response = self.view.list(self.request)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Language not supported', str(response.data))
        self.view.translate_response = original_translate_response

    def test_list_generic_exception(self):
        original_translate_response = self.view.translate_response
        def fake_translate_response(*a, **k):
            raise Exception('Unexpected error')
        self.view.translate_response = fake_translate_response
        self.view.request = self.request  # Fix: asignar self.request
        self.view.format_kwarg = None  # Fix: asignar format_kwarg
        response = self.view.list(self.request)
        self.assertEqual(response.status_code, 500)
        self.assertIn('unexpected', str(response.data['error']).lower())
        self.view.translate_response = original_translate_response