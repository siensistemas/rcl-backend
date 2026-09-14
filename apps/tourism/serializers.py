from rest_framework import serializers
from shared.validators import validate_upload_size, MAX_IMAGE_SIZE_MB
from .models import Attraction, TouristRoute


class AttractionSerializer(serializers.ModelSerializer):
    municipality_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Attraction
        fields = '__all__'
        read_only_fields = ['views_count', 'created_at', 'updated_at']

    def validate_image(self, image):
        if image is None:
            return image
        validate_upload_size(image, MAX_IMAGE_SIZE_MB, 'la imagen de la atracción')
        return image

    def get_municipality_name(self, obj):
        return obj.municipality.name if obj.municipality else None

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None


class TouristRouteSerializer(serializers.ModelSerializer):
    municipality_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    attraction_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = TouristRoute
        fields = '__all__'
        read_only_fields = ['views_count', 'created_at', 'updated_at']

    def validate_image(self, image):
        if image is None:
            return image
        validate_upload_size(image, MAX_IMAGE_SIZE_MB, 'la imagen de la ruta')
        return image

    def get_municipality_name(self, obj):
        return obj.municipality.name if obj.municipality else None

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None