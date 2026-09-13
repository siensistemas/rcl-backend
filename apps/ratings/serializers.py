from rest_framework import serializers
from .models import Rating


class RatingSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username