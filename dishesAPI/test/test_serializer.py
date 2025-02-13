from rest_framework.test import APITestCase
from ..models import Desk, Allergens, Ingredient, Dish, Order, OrderDish
from ..serializer import DeskSerializer, AllergensSerializer, IngredientSerializer, DishSerializer, OrderSerializer, OrderDishSerializer

class SerializerTestCase(APITestCase):

    def setUp(self):
        self.desk = Desk.objects.create(desk_number=1, capacity=4)
        self.allergen = Allergens.objects.create(allergen_name="Peanuts")  # Crear instancia de Allergens
        self.ingredient = Ingredient.objects.create(ingredient_name="Tomato", quantity=2)  # Crear instancia de Ingredient
        self.ingredient.allergen.set([self.allergen])  # Asignar allergen a ingredient

        self.desk_data = {'desk_number': 1, 'capacity': 4}
        self.allergens_data = {'allergen_name': 'Peanuts'}
        self.ingredient_data = {'ingredient_name': 'Tomato', 'quantity': 2, 'allergen': [self.allergen.id]}
        self.dish_data = {
            'dish_name': 'Pasta',
            'description': 'Delicious pasta with tomato sauce',
            'time_elaboration': '00:30:00',
            'price': 10,
            'link_ar': 'http://example.com/ar',
            'ingredient': [self.ingredient.id]
        }
        self.order_data = {
            'desk': self.desk.id,
            'date': '2023-10-10',
            'time': '12:00:00',
            'total_price': 20,
            'status': 'Pending'
        }

        self.dish = Dish.objects.create(
            dish_name=self.dish_data['dish_name'],
            description=self.dish_data['description'],
            time_elaboration=self.dish_data['time_elaboration'],
            price=self.dish_data['price'],
            link_ar=self.dish_data['link_ar']
        )
        self.dish.ingredient.set([self.ingredient])  # Use set() method to assign ingredients
        
        order_data_without_desk = self.order_data.copy()
        order_data_without_desk.pop('desk')
        self.order = Order.objects.create(desk=self.desk, **order_data_without_desk)
        
        self.order_dish = OrderDish.objects.create(order=self.order, dish=self.dish, quantity=1)

    def test_desk_serializer(self):
        serializer = DeskSerializer(data=self.desk_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, self.desk_data)

    def test_allergens_serializer(self):
        serializer = AllergensSerializer(data=self.allergens_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, self.allergens_data)

    def test_ingredient_serializer(self):
        serializer = IngredientSerializer(data=self.ingredient_data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        validated_data = serializer.validated_data
        validated_data['allergen'] = [allergen.id for allergen in validated_data['allergen']]
        self.assertEqual(validated_data, self.ingredient_data)

    def test_dish_serializer(self):
        serializer = DishSerializer(data=self.dish_data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        validated_data = serializer.validated_data
        validated_data['ingredient'] = [ingredient.id for ingredient in validated_data['ingredient']]
        validated_data['time_elaboration'] = validated_data['time_elaboration'].strftime('%H:%M:%S')
        
        expected_data = self.dish_data.copy()
        expected_data['ingredient'] = [self.ingredient.id]
        
        self.assertEqual(validated_data, expected_data)


    def test_order_serializer(self):
        serializer = OrderSerializer(data=self.order_data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        validated_data = serializer.validated_data
        validated_data['desk'] = validated_data['desk'].id
        validated_data['date'] = validated_data['date'].strftime('%Y-%m-%d')
        validated_data['time'] = validated_data['time'].strftime('%H:%M:%S')
        self.assertEqual(validated_data, self.order_data)

    def test_order_dish_serializer(self):
        serializer = OrderDishSerializer(data={'order': self.order.id, 'dish': self.dish.id, 'quantity': 1})
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        self.assertEqual(serializer.validated_data['order'].id, self.order.id)
        self.assertEqual(serializer.validated_data['dish'].id, self.dish.id)
        self.assertEqual(serializer.validated_data['quantity'], 1)
