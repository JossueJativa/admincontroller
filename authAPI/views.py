from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import update_last_login
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import jwt
from django.conf import settings
from datetime import datetime, timedelta

from .models import User
from .serializer import UserSerializer

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = []

    @swagger_auto_schema(method='post', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ))
    @action(detail=False, methods=['post'])
    def login(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            try:
                user = User.objects.get(username=username)
                if not check_password(password, user.password):
                    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            now = datetime.utcnow()
            iat = now - timedelta(seconds=10)  # Añadir margen de 10 segundos

            access_token = jwt.encode({
                'user_id': user.id,
                'exp': now + timedelta(minutes=60),
                'iat': iat,
                'type': 'access',
            }, settings.SECRET_KEY, algorithm='HS256')

            refresh_token = jwt.encode({
                'user_id': user.id,
                'exp': now + timedelta(days=7),
                'iat': iat,
                'type': 'refresh',
            }, settings.SECRET_KEY, algorithm='HS256')

            update_last_login(None, user)
            return Response({
                'access': access_token,
                'refresh': refresh_token,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(method='post', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ))
    @action(detail=False, methods=['post'], url_path='token/refresh', authentication_classes=[], permission_classes=[AllowAny])
    def token_refresh(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token required'}, status=400)
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'], leeway=10)
            if payload.get('type') != 'refresh':
                return Response({'error': 'Invalid token type'}, status=400)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Refresh token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=401)

        now = datetime.utcnow()
        iat = now - timedelta(seconds=10)

        access_token = jwt.encode({
            'user_id': payload['user_id'],
            'exp': now + timedelta(minutes=60),
            'iat': iat,
            'type': 'access'
        }, settings.SECRET_KEY, algorithm='HS256')

        return Response({'access': access_token}, status=200)
