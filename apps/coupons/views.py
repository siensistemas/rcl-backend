from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Coupon
from .serializers import CouponSerializer


class CouponViewSet(viewsets.ModelViewSet):
    serializer_class = CouponSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['promotion', 'status']
    search_fields = ['code']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Coupon.objects.filter(user=self.request.user)

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def redeem(self, request, pk=None):
        coupon = self.get_object()
        if coupon.user != request.user:
            return Response({'error': 'No tienes permisos'}, status=403)
        if coupon.status == 'used':
            return Response({'error': 'El cupon ya fue usado'}, status=400)
        if coupon.expires_at and coupon.expires_at < timezone.now():
            coupon.status = 'expired'
            coupon.save(update_fields=['status'])
            return Response({'error': 'El cupon expiro'}, status=400)
        coupon.status = 'used'
        coupon.redeemed_at = timezone.now()
        coupon.save(update_fields=['status', 'redeemed_at'])
        coupon.promotion.redeemed_count += 1
        coupon.promotion.save(update_fields=['redeemed_count'])
        return Response(self.get_serializer(coupon).data)