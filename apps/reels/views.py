from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Reel
from .serializers import ReelSerializer
from shared.permissions import IsMerchant
from shared.tenant import resolve_tenant_for_user


class ReelViewSet(viewsets.ModelViewSet):
    serializer_class = ReelSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['business', 'municipality', 'status', 'is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'views_count', 'likes_count']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and getattr(user, 'role', None) == 'merchant':
            qs = Reel.objects.filter(Q(status='published') | Q(business__owner=user))
        else:
            qs = Reel.objects.filter(status='published')
        tenant = resolve_tenant_for_user(user)
        if tenant is not None:
            qs = qs.filter(municipality=tenant)
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'publish', 'unpublish']:
            return [permissions.IsAuthenticated(), IsMerchant()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        business = serializer.validated_data.get('business')
        if business and business.owner != self.request.user:
            raise PermissionDenied('No eres el dueño de este comercio')
        serializer.save(
            municipality=resolve_tenant_for_user(self.request.user),
            business=business or getattr(self.request.user, 'default_business', None),
        )

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        reel = self.get_object()
        reel.views_count += 1
        reel.save(update_fields=['views_count'])
        return Response({'views': reel.views_count})

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        reel = self.get_object()
        reel.likes_count += 1
        reel.save(update_fields=['likes_count'])
        return Response({'likes': reel.likes_count})

    def _set_status(self, request, status_value):
        reel = self.get_object()
        if reel.business.owner != request.user:
            raise PermissionDenied('No eres el dueño de este comercio')
        reel.status = status_value
        reel.save(update_fields=['status', 'updated_at'])
        return Response(
            ReelSerializer(reel, context=self.get_serializer_context()).data
        )

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        return self._set_status(request, 'published')

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        return self._set_status(request, 'draft')