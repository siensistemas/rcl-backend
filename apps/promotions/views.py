from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Promotion
from .serializers import PromotionSerializer
from shared.permissions import IsMerchant, IsOwner
from shared.tenant import resolve_tenant_for_user

class PromotionViewSet(viewsets.ModelViewSet):
    serializer_class = PromotionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['business', 'status', 'is_featured', 'discount_type']
    search_fields = ['title', 'description', 'subtitle']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'views_count']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Promotion.objects.all()
        tenant = resolve_tenant_for_user(self.request.user)
        if tenant is not None:
            qs = qs.filter(business__municipality=tenant)
        return qs
    
    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsMerchant()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        business = serializer.validated_data.get('business')
        if business.owner != self.request.user:
            raise PermissionError('No eres el dueÃ±o de este comercio')
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        promotion = self.get_object()
        promotion.views_count += 1
        promotion.save(update_fields=['views_count'])
        return Response({'views': promotion.views_count})
    
    @action(detail=True, methods=['post'])
    def increment_click(self, request, pk=None):
        promotion = self.get_object()
        promotion.clicks_count += 1
        promotion.save(update_fields=['clicks_count'])
        return Response({'clicks': promotion.clicks_count})
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        from django.utils import timezone
        promotions = Promotion.objects.filter(
            status='active',
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )
        serializer = self.get_serializer(promotions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        promotions = Promotion.objects.filter(is_featured=True, status='active')
        serializer = self.get_serializer(promotions[:10], many=True)
        return Response(serializer.data)
