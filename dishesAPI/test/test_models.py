from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import Desk, Allergens, Ingredient, Dish, Order, OrderDish, Category, Garrison

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(category_name="Appetizers")

    def test_category_creation(self):
        self.assertEqual(self.category.category_name, "Appetizers")

    def test_category_creation_without_name(self):
        with self.assertRaises(ValidationError):
            category = Category()
            category.full_clean()

class DeskModelTest(TestCase):
    def setUp(self):
        self.desk = Desk.objects.create(desk_number=1, capacity=4)

    def test_desk_creation(self):
        self.assertEqual(self.desk.desk_number, 1)
        self.assertEqual(self.desk.capacity, 4)

    def test_desk_creation_without_capacity(self):
        with self.assertRaises(ValidationError):
            desk = Desk(desk_number=2)
            desk.full_clean()

class AllergensModelTest(TestCase):
    def setUp(self):
        self.allergen = Allergens.objects.create(allergen_name="Peanuts")

    def test_allergen_creation(self):
        self.assertEqual(self.allergen.allergen_name, "Peanuts")

    def test_allergen_creation_without_name(self):
        with self.assertRaises(ValidationError):
            allergen = Allergens()
            allergen.full_clean()

class IngredientModelTest(TestCase):
    def setUp(self):
        self.allergen = Allergens.objects.create(allergen_name="Peanuts")
        self.ingredient = Ingredient.objects.create(ingredient_name="Flour")
        self.ingredient.allergen.add(self.allergen)

    def test_ingredient_creation(self):
        self.assertEqual(self.ingredient.ingredient_name, "Flour")
        self.assertIn(self.allergen, self.ingredient.allergen.all())

    def test_ingredient_creation_without_name(self):
        with self.assertRaises(ValidationError):
            ingredient = Ingredient()
            ingredient.full_clean()

class DishModelTest(TestCase):
    def setUp(self):
        self.ingredient = Ingredient.objects.create(ingredient_name="Flour")
        self.category = Category.objects.create(category_name="Appetizers")
        self.dish_with_garrison = Dish.objects.create(
            dish_name="Pizza",
            description="Delicious pizza",
            time_elaboration="00:30:00",
            price=10,
            link_ar="http://example.com",
            category=self.category,
            has_garrison=True  # Dish with garrison
        )
        self.dish_without_garrison = Dish.objects.create(
            dish_name="Salad",
            description="Healthy salad",
            time_elaboration="00:15:00",
            price=5,
            link_ar="http://example.com",
            category=self.category,
            has_garrison=False  # Dish without garrison
        )
        self.dish_with_garrison.ingredient.add(self.ingredient)
        self.dish_without_garrison.ingredient.add(self.ingredient)

    def test_dish_creation(self):
        self.assertEqual(self.dish_with_garrison.dish_name, "Pizza")
        self.assertEqual(self.dish_with_garrison.description, "Delicious pizza")
        self.assertEqual(self.dish_with_garrison.time_elaboration, "00:30:00")
        self.assertEqual(self.dish_with_garrison.price, 10)
        self.assertEqual(self.dish_with_garrison.link_ar, "http://example.com")
        self.assertEqual(self.dish_with_garrison.category, self.category)
        self.assertIn(self.ingredient, self.dish_with_garrison.ingredient.all())

    def test_dish_creation_without_name(self):
        with self.assertRaises(ValidationError):
            dish = Dish(
                description="Delicious pizza", 
                time_elaboration="00:30:00", 
                price=10, 
                link_ar="http://example.com",
                category=self.category,
            )
            dish.full_clean()

    def test_dish_creation_with_garrison(self):
        self.assertTrue(self.dish_with_garrison.has_garrison)

    def test_dish_creation_without_garrison(self):
        self.assertFalse(self.dish_without_garrison.has_garrison)

class GarrisonModelTest(TestCase):
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

    def test_garrison_creation(self):
        self.assertEqual(self.garrison.garrison_name, "Fries")
        self.assertIn(self.dish, self.garrison.dish.all())

    def test_dish_garrison_relationship(self):
        self.assertIn(self.garrison, self.dish.garrisons.all())

class OrderModelTest(TestCase):
    def setUp(self):
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
        self.order_dish = OrderDish.objects.create(order=self.order, dish=self.dish, quantity=1)

    def test_order_creation(self):
        self.assertEqual(self.order.desk, self.desk)
        self.assertEqual(self.order.date, "2023-10-10")
        self.assertEqual(self.order.time, "12:00:00")
        self.assertEqual(self.order.total_price, 10)
        self.assertEqual(self.order.status, "Pending")
        self.assertIn(self.order_dish, self.order.orderdish_set.all())

    def test_order_creation_without_date(self):
        with self.assertRaises(ValidationError):
            order = Order(desk=self.desk, time="12:00:00", total_price=10, status="Pending")
            order.full_clean()

class OrderDishModelTest(TestCase):
    def setUp(self):
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
        self.order_dish = OrderDish.objects.create(order=self.order, dish=self.dish, quantity=2)

    def test_order_dish_creation(self):
        self.assertEqual(self.order_dish.order, self.order)
        self.assertEqual(self.order_dish.dish, self.dish)
        self.assertEqual(self.order_dish.quantity, 2)