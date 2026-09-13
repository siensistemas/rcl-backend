from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Ad
from .serializers import AdSerializer
from shared.permissions import IsMerchant
from shared.tenant import resolve_tenant_for_user


class AdViewSet(viewsets.ModelViewSet):
    serializer_class = AdSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['business', 'municipality', 'ad_type', 'placement', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'start_date', 'views_count']
    ordering = ['-created_at']

    ALLOWED_TRANSITIONS = {
        'draft': {'active', 'paused', 'ended'},
        'active': {'paused', 'ended'},
        'paused': {'active', 'ended'},
        'ended': set(),
    }

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()
        if user.is_authenticated and getattr(user, 'role', None) == 'merchant':
            qs = Ad.objects.filter(
                Q(business__owner=user)
                | Q(status='active', start_date__lte=now, end_date__gte=now)
            )
        else:
            qs = Ad.objects.filter(status='active', start_date__lte=now, end_date__gte=now)
        tenant = resolve_tenant_for_user(user)
        if tenant is not None:
            qs = qs.filter(municipality=tenant)
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'publish', 'pause']:
            return [permissions.IsAuthenticated(), IsMerchant()]
        return [permissions.AllowAny()]

    def _check_owner(self, ad):
        if ad.business and ad.business.owner != self.request.user:
            raise PermissionDenied('No eres el dueño de este negocio')

    def perform_create(self, serializer):
        business = serializer.validated_data.get('business')
        if business and business.owner != self.request.user:
            raise PermissionDenied('No eres el dueño de este comercio')
        serializer.save(
            municipality=resolve_tenant_for_user(self.request.user),
            business=business or getattr(self.request.user, 'default_business', None),
        )

    def perform_update(self, serializer):
        self._check_owner(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self._check_owner(instance)
        instance.delete()

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        ad = self.get_object()
        ad.views_count += 1
        ad.save(update_fields=['views_count'])
        return Response({'views': ad.views_count})

    @action(detail=True, methods=['post'])
    def increment_click(self, request, pk=None):
        ad = self.get_object()
        ad.clicks_count += 1
        ad.save(update_fields=['clicks_count'])
        return Response({'clicks': ad.clicks_count})

    def _set_status(self, request, target):
        ad = self.get_object()
        self._check_owner(ad)
        if target not in self.ALLOWED_TRANSITIONS.get(ad.status, set()):
            raise ValidationError({
                'status': f'No se puede pasar de {ad.status} a {target}'
            })
        ad.status = target
        ad.save(update_fields=['status', 'updated_at'])
        return Response(
            AdSerializer(ad, context=self.get_serializer_context()).data
        )

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        return self._set_status(request, 'active')

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        return self._set_status(request, 'paused')

    @action(detail=False, methods=['get'])
    def active(self, request):
        placement = request.query_params.get('placement', 'home')
        ads = Ad.objects.filter(
            status='active',
            placement=placement,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
        )
        serializer = self.get_serializer(ads, many=True)
        return Response(serializer.data)