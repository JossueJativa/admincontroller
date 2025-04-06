from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import (
    Desk, Allergens, Ingredient, Dish, Order, OrderDish, 
    Category, Garrison, Invoice, InvoiceDish
)
from .serializer import (
    CategorySerializer, DeskSerializer, AllergensSerializer,
    IngredientSerializer, DishSerializer, GarrisonSerializer,
    OrderSerializer, OrderDishSerializer, InvoiceSerializer,
    InvoiceDishSerializer
)

class BaseProtectedViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def partial_update(self, request, *args, **kwargs):
        return Response({'error': 'Method not allowed'}, status=405)

class CategoryViewSet(BaseProtectedViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class DeskViewSet(BaseProtectedViewSet):
    queryset = Desk.objects.all()
    serializer_class = DeskSerializer

class AllergensViewSet(BaseProtectedViewSet):
    queryset = Allergens.objects.all()
    serializer_class = AllergensSerializer

class IngredientViewSet(BaseProtectedViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class DishViewSet(BaseProtectedViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer

class GarrisonViewSet(BaseProtectedViewSet):
    queryset = Garrison.objects.all()
    serializer_class = GarrisonSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

class OrderDishViewSet(viewsets.ModelViewSet):
    queryset = OrderDish.objects.all()
    serializer_class = OrderDishSerializer
    permission_classes = [AllowAny]

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [AllowAny]

class InvoiceDishViewSet(viewsets.ModelViewSet):
    queryset = InvoiceDish.objects.all()
    serializer_class = InvoiceDishSerializer
    permission_classes = [AllowAny]