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

    def validate(self, attrs):
        dtype = attrs.get('discount_type')
        value = attrs.get('discount_value')
        if value is not None and value < 0:
            raise serializers.ValidationError(
                {'discount_value': 'El valor del descuento no puede ser negativo.'}
            )
        if dtype == 'percentage' and value is not None and value > 100:
            raise serializers.ValidationError(
                {'discount_value': 'El porcentaje debe estar entre 1 y 100.'}
            )
        return attrs
