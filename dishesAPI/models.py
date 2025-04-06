from django.db import models

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=100)

class Desk(models.Model):
    desk_number = models.IntegerField()
    capacity = models.IntegerField()

class Allergens(models.Model):
    allergen_name = models.CharField(max_length=100)

class Ingredient(models.Model):
    ingredient_name = models.CharField(max_length=100)
    allergen = models.ManyToManyField(Allergens)

class Dish(models.Model):
    dish_name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    time_elaboration = models.TimeField()
    price = models.FloatField()
    ingredient = models.ManyToManyField(Ingredient)
    link_ar = models.CharField(max_length=1000)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    has_garrison = models.BooleanField(default=False)

class Garrison(models.Model):
    garrison_name = models.CharField(max_length=100)
    dish = models.ManyToManyField(Dish, related_name='garrisons')

class Order(models.Model):
    desk = models.ForeignKey(Desk, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    total_price = models.FloatField()
    status = models.CharField(max_length=100)
    order_dish = models.ManyToManyField(Dish, through='OrderDish')

class OrderDish(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

class Invoice(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=100)
    total_price = models.FloatField()

class InvoiceDish(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)