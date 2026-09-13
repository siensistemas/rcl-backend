from rest_framework import serializers
from shared.validators import validate_reel_video
from .models import Reel


class ReelSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()
    municipality_name = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Reel
        fields = '__all__'
        read_only_fields = ['views_count', 'likes_count', 'created_at', 'updated_at']
        validators = []

    def validate_video(self, video):
        if video is None:
            raise serializers.ValidationError(
                'El video es obligatorio (MP4, máximo 7 segundos y 50 MB)'
            )
        validate_reel_video(video)
        return video

    def get_business_name(self, obj):
        return obj.business.name

    def get_municipality_name(self, obj):
        return obj.municipality.name if obj.municipality else None

    def get_video_url(self, obj):
        return obj.video.url if obj.video else None

    def get_thumbnail_url(self, obj):
        return obj.thumbnail.url if obj.thumbnail else None

    def get_is_active(self, obj):
        return obj.status == 'published'