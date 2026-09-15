from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job
from .serializers import JobSerializer
from shared.permissions import IsAdminOrMerchant, IsOwnerOrAdmin
from shared.tenant import resolve_request_tenant


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['business', 'municipality', 'job_type', 'work_mode', 'status', 'is_featured']
    search_fields = ['title', 'description', 'requirements']
    ordering_fields = ['created_at', 'salary_max', 'views_count']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Job.objects.all()
        tenant = resolve_request_tenant(self.request)
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
        job = self.get_object()
        job.status = 'published'
        job.save(update_fields=['status'])
        return Response({'status': job.status})

    @action(detail=True, methods=['post'], url_path='unpublish')
    def unpublish(self, request, pk=None):
        job = self.get_object()
        job.status = 'draft'
        job.save(update_fields=['status'])
        return Response({'status': job.status})

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        job = self.get_object()
        job.views_count += 1
        job.save(update_fields=['views_count'])
        return Response({'views': job.views_count})

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        job = self.get_object()
        job.applications_count += 1
        job.save(update_fields=['applications_count'])
        return Response({'applications': job.applications_count})