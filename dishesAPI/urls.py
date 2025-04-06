from django.urls import path, include
from rest_framework import routers
from .views import (
    DeskViewSet, AllergensViewSet, IngredientViewSet,
    DishViewSet, OrderViewSet, OrderDishViewSet,
    CategoryViewSet, GarrisonViewSet,
    InvoiceViewSet, InvoiceDishViewSet
)

router = routers.DefaultRouter()
router.register(r'desk', DeskViewSet)
router.register(r'allergens', AllergensViewSet)
router.register(r'ingredient', IngredientViewSet)
router.register(r'dish', DishViewSet)
router.register(r'order', OrderViewSet)
router.register(r'orderdish', OrderDishViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'garrison', GarrisonViewSet)
router.register(r'invoice', InvoiceViewSet)
router.register(r'invoicedish', InvoiceDishViewSet)

urlpatterns = [
    path('', include(router.urls)),
]