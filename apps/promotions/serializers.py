from rest_framework import serializers
from .models import Promotion

class PromotionSerializer(serializers.ModelSerializer):
    remaining_quantity = serializers.IntegerField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    usage_percentage = serializers.FloatField(read_only=True)
    business_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Promotion
        fields = '__all__'
        read_only_fields = ['views_count', 'redeemed_count', 'clicks_count', 'share_count', 'created_at', 'updated_at']
    
    def get_business_name(self, obj):
        return obj.business.name
