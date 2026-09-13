from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event
from .serializers import EventSerializer
from shared.permissions import IsAdminOrMerchant, IsOwnerOrAdmin
from shared.tenant import resolve_tenant_for_user


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['business', 'municipality', 'event_type', 'status', 'is_featured']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_date', 'created_at', 'views_count']
    ordering = ['-start_date']

    def get_queryset(self):
        qs = Event.objects.all()
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
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'publish', 'unpublish']:
            return [permissions.IsAuthenticated(), IsAdminOrMerchant(), IsOwnerOrAdmin()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        if self.request.data.get('municipality'):
            serializer.save()
        else:
            serializer.save(municipality=resolve_tenant_for_user(self.request.user))

    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, pk=None):
        event = self.get_object()
        event.status = 'published'
        event.save(update_fields=['status'])
        return Response({'status': event.status})

    @action(detail=True, methods=['post'], url_path='unpublish')
    def unpublish(self, request, pk=None):
        event = self.get_object()
        event.status = 'draft'
        event.save(update_fields=['status'])
        return Response({'status': event.status})

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        event = self.get_object()
        event.views_count += 1
        event.save(update_fields=['views_count'])
        return Response({'views': event.views_count})

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        from django.utils import timezone
        events = Event.objects.filter(status='published', end_date__gte=timezone.now())
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)