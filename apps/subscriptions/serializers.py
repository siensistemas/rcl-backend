from rest_framework import serializers
from .models import Plan, Subscription

class PlanSerializer(serializers.ModelSerializer):
    is_free = serializers.BooleanField(read_only=True)
    price_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = Plan
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    plan_name = serializers.SerializerMethodField()
    business_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_plan_name(self, obj):
        return obj.plan.name
    
    def get_business_name(self, obj):
        return obj.business.name
