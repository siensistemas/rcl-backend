from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'is_read']

    def get_business_name(self, obj):
        return obj.business.name if obj.business else None