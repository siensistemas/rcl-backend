from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Plan, Subscription
from .serializers import PlanSerializer, SubscriptionSerializer
from shared.permissions import IsGlobalAdmin, IsMerchant
from shared.tenant import resolve_tenant_for_user

class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer

    def get_queryset(self):
        qs = Plan.objects.filter(is_active=True)
        tenant = resolve_tenant_for_user(self.request.user)
        if tenant is not None:
            qs = qs.filter(municipality=tenant)
        return qs
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsGlobalAdmin()]
        return [permissions.AllowAny()]

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        qs = Subscription.objects.all()
        tenant = resolve_tenant_for_user(self.request.user)
        if tenant is not None:
            qs = qs.filter(business__municipality=tenant)
        return qs
    
    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsMerchant()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        subscription.status = 'cancelled'
        subscription.save()
        return Response({'message': 'Suscripcion cancelada'})
    
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        from django.utils import timezone
        subscription = self.get_object()
        # Implement renewal logic
        return Response({'message': 'Suscripcion renovada'})
