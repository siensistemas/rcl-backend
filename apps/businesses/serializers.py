from rest_framework import serializers
from shared.validators import validate_upload_size, MAX_IMAGE_SIZE_MB, MAX_REEL_SIZE_MB
from .models import Business, BusinessMedia, BusinessHours

class BusinessHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessHours
        fields = ['id', 'day', 'open_time', 'close_time', 'is_closed']

class BusinessMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessMedia
        fields = ['id', 'media_type', 'file', 'thumbnail', 'title', 'description', 
                  'is_cover', 'is_featured', 'order', 'views_count', 'created_at']
        read_only_fields = ['views_count', 'created_at', 'updated_at']

    def validate(self, attrs):
        media_type = attrs.get('media_type') or getattr(self.instance, 'media_type', None) or 'image'
        file = attrs.get('file')
        if file is not None:
            if media_type == 'video':
                validate_upload_size(file, MAX_REEL_SIZE_MB, 'el video')
            else:
                validate_upload_size(file, MAX_IMAGE_SIZE_MB, 'la imagen')
        return attrs

class BusinessSerializer(serializers.ModelSerializer):
    media = BusinessMediaSerializer(many=True, read_only=True)
    hours = BusinessHoursSerializer(many=True, read_only=True)
    rating_average = serializers.FloatField(read_only=True)
    total_ratings = serializers.IntegerField(read_only=True)
    is_open_now = serializers.BooleanField(read_only=True)
    plan_name = serializers.CharField(read_only=True)
    plan_type = serializers.CharField(read_only=True)
    owner_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    municipality_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Business
        fields = '__all__'
        read_only_fields = [
            'slug', 'views_count', 'clicks_count', 'whatsapp_clicks', 
            'call_clicks', 'direction_clicks', 'website_clicks', 
            'social_clicks', 'favorite_count', 'share_count',
            'created_at', 'updated_at'
        ]
    
    def get_owner_name(self, obj):
        return obj.owner.get_full_name()
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
    
    def get_municipality_name(self, obj):
        return obj.municipality.name

class BusinessCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            'name', 'description', 'address', 'latitude', 'longitude',
            'phone', 'whatsapp', 'email', 'website', 'category', 'subcategory',
            'schedule', 'features', 'services', 'payment_methods', 'municipality'
        ]

class BusinessUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'
        read_only_fields = ['slug', 'owner', 'views_count', 'created_at', 'updated_at']
