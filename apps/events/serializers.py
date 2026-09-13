from rest_framework import serializers
from shared.validators import validate_upload_size, MAX_IMAGE_SIZE_MB
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()
    municipality_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['views_count', 'created_at', 'updated_at']

    def validate_image(self, image):
        if image is None:
            return image
        validate_upload_size(image, MAX_IMAGE_SIZE_MB, 'la imagen del evento')
        return image

    def get_business_name(self, obj):
        return obj.business.name if obj.business else None

    def get_municipality_name(self, obj):
        return obj.municipality.name if obj.municipality else None

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

    def get_is_active(self, obj):
        from django.utils import timezone
        return obj.status == 'published' and obj.start_date <= timezone.now() <= obj.end_date