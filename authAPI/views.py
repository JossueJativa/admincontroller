from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import update_last_login

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User
from .serializer import UserSerializer

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(method='post', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ))
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user_password = User.objects.get(username=username).password
        if not check_password(password, user_password):
            return Response({'error': 'Invalid credentials'}, status=400)
        
        user = User.objects.get(username=username)
        refresh = RefreshToken.for_user(user)
        update_last_login(None, user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    
    @swagger_auto_schema(method='post', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ))
    @action(detail=False, methods=['post'])
    def register(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=400)
        user = User.objects.create(username=username, password=make_password(password))
        user.save()
        return Response({'success': 'User created'}, status=201)
    
    # Logout
    @swagger_auto_schema(method='post', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ))
    @action(detail=False, methods=['post'])
    def logout(self, request):
        data = request.data
        refresh = data.get('refresh')

        if not refresh:
            return Response({'error': 'Refresh token is required'}, status=400)

        try:
            RefreshToken(refresh).blacklist()
        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response({'success': 'User logged out'}, status=200)