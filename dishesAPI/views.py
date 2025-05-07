from datetime import datetime
import os
import deepl
import re
import logging
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from dotenv import load_dotenv
from django.db.models import Sum, Count
from rest_framework.decorators import action

load_dotenv()

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

# Ampliar la lista de idiomas soportados
SUPPORTED_LANGUAGES = ["EN-GB", "EN-US", "ES", "FR", "DE", "IT", "NL", "PL", "PT", "RU", "JA", "ZH"]

# Configurar el logger
logger = logging.getLogger(__name__)

# Mapeo de idiomas obsoletos a los nuevos valores
LANGUAGE_MAPPING = {
    "EN": "EN-GB",  # Cambiar EN a EN-GB por defecto
}

def translate_fields(data, fields, target_lang):
    auth_key = os.getenv("DEEPL_AUTH_KEY")
    if not auth_key:
        logger.error("DeepL API key is not configured.")
        raise ValueError("DeepL API key is not configured.")

    translator = deepl.Translator(auth_key)

    try:
        for item in data:
            translations = translator.translate_text(
                [item[field] for field in fields], target_lang=target_lang
            )
            for i, field in enumerate(fields):
                item[field] = translations[i].text
    except deepl.exceptions.DeepLException as e:
        logger.error(f"DeepL API error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

class BaseProtectedViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def partial_update(self, request, *args, **kwargs):
        return Response({'error': 'Method not allowed'}, status=405)

    def translate_response(self, data, fields, request):
        target_lang = request.query_params.get('lang', 'ES').upper()
        target_lang = re.sub(r'[^A-Z-]', '', target_lang.strip())
        target_lang = LANGUAGE_MAPPING.get(target_lang, target_lang)

        if target_lang not in SUPPORTED_LANGUAGES:
            logger.error("Unsupported language: %s", target_lang)
            raise ValueError(f"Language '{target_lang}' not supported.")

        if target_lang != 'ES':
            translate_fields(data, fields, target_lang)

class CategoryViewSet(BaseProtectedViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        try:
            self.translate_response(data, ['category_name'], request)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=500)

        return Response(data)

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        try:
            self.translate_response([data], ['dish_name', 'description'], request)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=500)

        return Response(data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        try:
            self.translate_response(data, ['dish_name', 'description'], request)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=500)

        return Response(data)

class GarrisonViewSet(BaseProtectedViewSet):
    queryset = Garrison.objects.all()
    serializer_class = GarrisonSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        try:
            self.translate_response([data], ['garrison_name'], request)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=500)

        return Response(data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        try:
            self.translate_response(data, ['garrison_name'], request)
            print('Garrison data:', data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=500)

        return Response(data)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def unified_statistics(self, request):
        try:
            year = request.query_params.get('year', datetime.now().year)
            month = request.query_params.get('month', datetime.now().month)

            # Eliminate characters that are not digits
            year = re.sub(r'[^0-9]', '', str(year))
            month = re.sub(r'[^0-9]', '', str(month))

            filtered_orders = Order.objects.filter(
                date__year=year,
                date__month=month
            )

            total_dishes = filtered_orders.aggregate(total_dishes=Sum('orderdish__quantity'))['total_dishes'] or 0
            total_revenue = filtered_orders.aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0
            average_dishes_per_table = (
                total_dishes / filtered_orders.count()
                if filtered_orders.exists() else 0
            )

            dish_counts = (
                OrderDish.objects.filter(order__in=filtered_orders)
                .values('dish__dish_name')
                .annotate(count=Sum('quantity'))
                .order_by('-count')
            )

            category_counts = (
                OrderDish.objects.filter(order__in=filtered_orders)
                .values('dish__category__category_name')
                .annotate(count=Sum('quantity'))
                .order_by('-count')
            )

            return Response({
                'dashboard_statistics': {
                    'total_dishes': total_dishes,
                    'total_revenue': total_revenue,
                    'average_dishes_per_table': round(average_dishes_per_table, 2),
                    'dishes': list(dish_counts),
                    'categories': list(category_counts),
                }
            })
        except Exception as e:
            logger.error(f"Error in unified_statistics endpoint: {str(e)}")
            return Response({'error': str(e)}, status=500)

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