from rest_framework import serializers
from .models import ConsentRecord, RightsRequest, DataExportRequest, AccountDeletionRequest


class ConsentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentRecord
        fields = '__all__'
        read_only_fields = ['user', 'timestamp', 'revoked_at']


class RightsRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RightsRequest
        fields = '__all__'
        read_only_fields = ['user', 'status', 'created_at']


class DataExportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataExportRequest
        fields = '__all__'
        read_only_fields = ['user', 'status', 'requested_at', 'file']


class AccountDeletionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDeletionRequest
        fields = '__all__'
        read_only_fields = ['user', 'status', 'requested_at', 'scheduled_date']