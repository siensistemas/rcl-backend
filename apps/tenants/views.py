from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Municipality
from .serializers import MunicipalitySerializer
from shared.permissions import IsGlobalAdmin, IsMunicipalAdmin

class MunicipalityViewSet(viewsets.ModelViewSet):
    queryset = Municipality.objects.filter(is_active=True)
    serializer_class = MunicipalitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_public']
    search_fields = ['name', 'description', 'slug']
    ordering_fields = ['name', 'created_at', 'total_businesses']
    ordering = ['name']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsGlobalAdmin()]
        return [permissions.AllowAny()]
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        municipality = self.get_object()
        return Response({
            'total_businesses': municipality.total_businesses,
            'total_users': municipality.total_users,
            'total_events': municipality.total_events,
            'total_promotions': municipality.total_promotions,
            'views_count': municipality.views_count,
        })
