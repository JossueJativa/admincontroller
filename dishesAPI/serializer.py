from rest_framework import serializers
from .models import (
    Desk,
    Allergens,
    Ingredient,
    Dish,
    Order,
    OrderDish,
    Category,
    Garrison
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class DeskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Desk
        fields = '__all__'

class AllergensSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergens
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'

class GarrisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garrison
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    dishes = DishSerializer(many=True, read_only=True)  # Incluir el campo dishes

    class Meta:
        model = Order
        fields = '__all__'

class OrderDishSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDish
        fields = '__all__'