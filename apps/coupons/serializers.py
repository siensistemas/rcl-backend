from rest_framework import serializers
from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    promotion_title = serializers.SerializerMethodField()
    business_name = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'redeemed_at']

    def get_promotion_title(self, obj):
        return obj.promotion.title

    def get_business_name(self, obj):
        return obj.promotion.business.name