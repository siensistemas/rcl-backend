from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category
from .serializers import CategorySerializer
from shared.permissions import IsGlobalAdmin
from shared.tenant import resolve_tenant_for_user

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['municipality', 'parent', 'is_active', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name', 'total_businesses']
    ordering = ['order', 'name']

    def get_queryset(self):
        qs = Category.objects.filter(is_active=True)
        tenant = resolve_tenant_for_user(self.request.user)
        if tenant is not None:
            qs = qs.filter(municipality=tenant)
        return qs
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
