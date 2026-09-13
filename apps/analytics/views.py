from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncDate
from .models import AnalyticEvent
from .serializers import AnalyticEventSerializer
from apps.businesses.models import Business


class AnalyticViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        business_id = request.query_params.get('business')
        try:
            days = int(request.query_params.get('days', 7))
        except (TypeError, ValueError):
            days = 7
        if days < 1 or days > 365:
            days = 7

        qs = AnalyticEvent.objects.filter(business__owner=request.user)
        if business_id:
            qs = qs.filter(business_id=business_id)

        since = timezone.now() - timezone.timedelta(days=days)
        qs = qs.filter(created_at__gte=since)

        by_type = list(
            qs.values('event_type')
            .annotate(total=Count('id'))
            .order_by('event_type')
        )

        daily = list(
            qs.annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(total=Count('id'))
            .order_by('day')
        )

        summary = qs.values('business_id').annotate(
            views_total=Count('id', filter=models.Q(event_type='view')),
            clicks_total=Count('id', filter=models.Q(event_type='click')),
            claims_total=Count('id', filter=models.Q(event_type='claim')),
        )

        return Response({
            'by_type': by_type,
            'daily': daily,
            'per_business': list(summary),
        })

    @action(detail=False, methods=['post'])
    def track(self, request):
        business_id = request.data.get('business')
        event_type = request.data.get('event_type')
        if not business_id or not event_type:
            return Response({'error': 'business y event_type requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        business = Business.objects.filter(pk=business_id, is_active=True).first()
        if not business:
            return Response({'error': 'Comercio no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        AnalyticEvent.objects.create(
            business=business,
            event_type=event_type,
            source=request.data.get('source', 'app'),
            meta=request.data.get('meta', {}),
            user=request.user if request.user.is_authenticated else None,
        )
        return Response({'success': True})