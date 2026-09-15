from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import User
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    UserUpdateSerializer, UserChangePasswordSerializer
)
from shared.tenant import get_current_tenant, resolve_tenant_for_user

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        # Solo administradores ven listados; un user normal solo se ve a si mismo
        if not user.is_authenticated:
            return User.objects.none()
        if user.role == 'global_admin':
            return User.objects.all()
        if user.role in ('municipal_admin', 'moderator', 'merchant', 'employee'):
            tenant = resolve_tenant_for_user(user)
            if tenant is not None:
                return User.objects.filter(municipality=tenant)
        return User.objects.filter(id=user.id)

    def get_permissions(self):
        if self.action in ['register', 'login', 'verify_email']:
            return [permissions.AllowAny()]
        elif self.action in ['change_password', 'me', 'update_profile', 'logout']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegistrationSerializer
        elif self.action == 'login':
            return UserLoginSerializer
        elif self.action in ['update', 'partial_update', 'update_profile']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return UserChangePasswordSerializer
        return UserSerializer
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        # Un cliente registrandose solo (sin municipality en el payload) toma
        # el municipio que eligio en la app via header X-Tenant-ID
        if 'municipality' not in data:
            tenant = get_current_tenant()
            if tenant is not None:
                data['municipality'] = tenant.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        return Response({
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'token_type': 'Bearer',
            'expires_in': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        return Response({
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'token_type': 'Bearer',
            'expires_in': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
            'user': UserSerializer(user).data,
        })
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Sesion cerrada exitosamente'})
        except Exception:
            return Response({'error': 'Token invalido'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not check_password(serializer.validated_data['old_password'], user.password):
            return Response({'error': 'ContraseÃ±a actual incorrecta'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'ContraseÃ±a actualizada exitosamente'})
    
    @action(detail=True, methods=['post'])
    def verify_email(self, request, pk=None):
        user = get_object_or_404(User, id=pk)
        code = request.data.get('code')
        if user.verification_code == code:
            user.email_verified = True
            user.is_verified = True
            user.verification_code = None
            user.save()
            return Response({'message': 'Email verificado exitosamente'})
        return Response({'error': 'Codigo invalido'}, status=status.HTTP_400_BAD_REQUEST)
