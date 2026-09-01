from rest_framework import serializers
from django.db.models import Sum

from apps.businesses.models import Business


class MerchantBusinessSerializer(serializers.ModelSerializer):
    """Serializa los comercios del panel del comerciante con las claves
    que espera la app Flutter (merchant_business_model.dart)."""

    category = serializers.SerializerMethodField()
    latitude = serializers.FloatField(allow_null=True, default=None)
    longitude = serializers.FloatField(allow_null=True, default=None)
    logo_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    promotion_count = serializers.SerializerMethodField()
    view_count = serializers.SerializerMethodField()
    claim_count = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = [
            'id', 'name', 'description', 'category', 'address',
            'latitude', 'longitude', 'phone', 'website',
            'logo_url', 'cover_url', 'is_active', 'is_verified',
            'promotion_count', 'view_count', 'claim_count', 'created_at',
        ]

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_logo_url(self, obj):
        return obj.logo.url if obj.logo else None

    def get_cover_url(self, obj):
        return obj.cover.url if obj.cover else None

    def get_promotion_count(self, obj):
        return obj.promotions.filter(status='active').count()

    def get_view_count(self, obj):
        return obj.views_count

    def get_claim_count(self, obj):
        return obj.promotions.aggregate(total=Sum('redeemed_count'))['total'] or 0