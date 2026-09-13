from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from .models import Rating
from .serializers import RatingSerializer


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['business']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        return Rating.objects.filter(business__is_active=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        # unique_together (business, user): volver a calificar actualiza en lugar de 500
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating, created = Rating.objects.update_or_create(
            business=serializer.validated_data['business'],
            user=request.user,
            defaults={
                'rating': serializer.validated_data.get('rating', 5),
                'comment': serializer.validated_data.get('comment', ''),
            },
        )
        return Response(
            RatingSerializer(rating).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        business_id = request.query_params.get('business')
        if not business_id:
            return Response({'error': 'business requerido'}, status=400)
        ratings = Rating.objects.filter(business_id=business_id)
        average = ratings.aggregate(avg=Avg('rating'))['avg'] or 0
        return Response({
            'average': round(average, 2),
            'total': ratings.count(),
        })