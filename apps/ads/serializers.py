from rest_framework import serializers
from shared.validators import validate_upload_size, MAX_IMAGE_SIZE_MB, MAX_REEL_SIZE_MB
from .models import Ad


class AdSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = '__all__'
        read_only_fields = ['views_count', 'clicks_count', 'created_at', 'updated_at']

    def validate_image(self, image):
        if image is None:
            return image
        validate_upload_size(image, MAX_IMAGE_SIZE_MB, 'la imagen del anuncio')
        return image

    def validate_video(self, video):
        if video is None:
            return video
        validate_upload_size(video, MAX_REEL_SIZE_MB, 'el video del anuncio')
        return video

    def get_business_name(self, obj):
        return obj.business.name if obj.business else None

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

    def get_video_url(self, obj):
        return obj.video.url if obj.video else None

    def get_is_active(self, obj):
        from django.utils import timezone
        return obj.status == 'active' and obj.start_date <= timezone.now() <= obj.end_date