from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import ConsentRecord, RightsRequest, DataExportRequest, AccountDeletionRequest
from .serializers import (
    ConsentRecordSerializer,
    RightsRequestSerializer,
    DataExportRequestSerializer,
    AccountDeletionRequestSerializer,
)


class ConsentViewSet(viewsets.GenericViewSet):
    queryset = ConsentRecord.objects.all()
    serializer_class = ConsentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        records = ConsentRecord.objects.filter(user=request.user)
        serializer = ConsentRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        records = ConsentRecord.objects.filter(user=request.user)
        serializer = ConsentRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def revoke(self, request):
        purpose = request.data.get('purpose')
        if not purpose:
            return Response({'error': 'purpose requerido'}, status=status.HTTP_400_BAD_REQUEST)
        latest = (
            ConsentRecord.objects
            .filter(user=request.user, purpose=purpose, granted=True, revoked_at__isnull=True)
            .first()
        )
        if latest is not None:
            latest.revoked_at = timezone.now()
            latest.save(update_fields=['revoked_at'])
        ConsentRecord.objects.create(
            user=request.user,
            purpose=purpose,
            granted=False,
            mechanism='revoke',
        )
        return Response({'message': 'Consentimiento revocado'})


class SubmitRightsRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RightsRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RequestDataExportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        obj = DataExportRequest.objects.create(user=request.user)
        return Response(
            DataExportRequestSerializer(obj).data,
            status=status.HTTP_201_CREATED,
        )


class RequestAccountDeletionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        obj = AccountDeletionRequest.objects.create(
            user=request.user,
            scheduled_date=timezone.now() + timezone.timedelta(days=7),
        )
        return Response(
            AccountDeletionRequestSerializer(obj).data,
            status=status.HTTP_201_CREATED,
        )