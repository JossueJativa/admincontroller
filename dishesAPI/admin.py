from django.contrib import admin

from .models import Desk, Allergens, Ingredient, Dish, Order, OrderDish

# Register your models here.
admin.site.register(Desk)
admin.site.register(Allergens)
admin.site.register(Ingredient)
admin.site.register(Dish)
admin.site.register(Order)
admin.site.register(OrderDish)