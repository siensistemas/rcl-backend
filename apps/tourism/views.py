from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from .models import Attraction, TouristRoute
from .serializers import AttractionSerializer, TouristRouteSerializer
from shared.permissions import IsAdminOrMerchant, IsAdmin
from shared.tenant import resolve_tenant_for_user


class AttractionViewSet(viewsets.ModelViewSet):
    serializer_class = AttractionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['municipality', 'attraction_type', 'status', 'is_featured']
    search_fields = ['name', 'description', 'address']
    ordering_fields = ['name', 'views_count', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        qs = Attraction.objects.all()
        tenant = resolve_tenant_for_user(self.request.user)
        if tenant is not None:
            qs = qs.filter(municipality=tenant)
        user = self.request.user
        is_privileged = (
            user.is_authenticated
            and user.role in ('merchant', 'global_admin', 'municipal_admin')
        )
        if not is_privileged:
            qs = qs.filter(status='published')
        return qs

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsAdminOrMerchant()]
        if self.action in ['update', 'partial_update', 'destroy', 'publish', 'unpublish']:
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        if self.request.data.get('municipality'):
            serializer.save()
        else:
            serializer.save(municipality=resolve_tenant_for_user(self.request.user))

    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, pk=None):
        attraction = self.get_object()
        attraction.status = 'published'
        attraction.save(update_fields=['status'])
        return Response({'status': attraction.status})

    @action(detail=True, methods=['post'], url_path='unpublish')
    def unpublish(self, request, pk=None):
        attraction = self.get_object()
        attraction.status = 'draft'
        attraction.save(update_fields=['status'])
        return Response({'status': attraction.status})

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        attraction = self.get_object()
        attraction.views_count += 1
        attraction.save(update_fields=['views_count'])
        return Response({'views': attraction.views_count})


class TouristRouteViewSet(viewsets.ModelViewSet):
    serializer_class = TouristRouteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['municipality', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        qs = TouristRoute.objects.annotate(attraction_count=models.Count('attractions'))
        tenant = resolve_tenant_for_user(self.request.user)
        if tenant is not None:
            qs = qs.filter(municipality=tenant)
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        if self.request.data.get('municipality'):
            serializer.save()
        else:
            serializer.save(municipality=resolve_tenant_for_user(self.request.user))

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        route = self.get_object()
        route.views_count += 1
        route.save(update_fields=['views_count'])
        return Response({'views': route.views_count})