from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Business, BusinessMedia, BusinessHours
from .serializers import BusinessSerializer, BusinessCreateSerializer, BusinessUpdateSerializer, BusinessMediaSerializer
from shared.permissions import IsMerchant, IsOwner, IsVerified
from shared.tenant import resolve_tenant_for_user

class BusinessViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['municipality', 'category', 'subcategory', 'is_verified', 'is_featured', 'is_active']
    search_fields = ['name', 'description', 'address', 'neighborhood', 'short_name']
    ordering_fields = ['name', 'views_count', 'rating_average', 'created_at']
    ordering = ['-views_count', 'name']

    def get_queryset(self):
        qs = Business.objects.filter(is_active=True, is_approved=True)
        tenant = resolve_tenant_for_user(self.request.user)
        if tenant is not None:
            qs = qs.filter(municipality=tenant)
        return qs
    
    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsMerchant(), IsVerified()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.AllowAny()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BusinessCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BusinessUpdateSerializer
        return BusinessSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_businesses(self, request):
        businesses = Business.all_objects.filter(owner=request.user, is_active=True)
        serializer = self.get_serializer(businesses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_media(self, request, pk=None):
        business = self.get_object()
        if business.owner != request.user:
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = BusinessMediaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(business=business)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        business = self.get_object()
        business.views_count += 1
        business.save(update_fields=['views_count'])
        return Response({'views': business.views_count})
    
    @action(detail=True, methods=['post'])
    def increment_click(self, request, pk=None):
        click_type = request.data.get('type')
        business = self.get_object()
        
        click_mapping = {
            'whatsapp': 'whatsapp_clicks',
            'call': 'call_clicks',
            'direction': 'direction_clicks',
            'website': 'website_clicks',
            'social': 'social_clicks',
        }
        
        if click_type in click_mapping:
            field = click_mapping[click_type]
            setattr(business, field, getattr(business, field) + 1)
            business.save(update_fields=[field])
            return Response({'success': True})
        
        return Response({'error': 'Tipo de click invalido'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        business = self.get_object()
        # Implement favorite logic
        return Response({'message': 'Favorito agregado'})
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = request.query_params.get('radius', 5)
        
        if not lat or not lng:
            return Response({'error': 'Latitud y longitud requeridas'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Simple nearby implementation (you can optimize with GIS)
        businesses = self.get_queryset()
        nearby = []
        for business in businesses:
            if business.latitude and business.longitude:
                # Calculate distance (simplified)
                # In production, use PostGIS or geopy
                nearby.append(business)
        
        serializer = self.get_serializer(nearby[:20], many=True)
        return Response(serializer.data)
