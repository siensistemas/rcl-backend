from rest_framework import serializers
from .models import Municipality

class MunicipalitySerializer(serializers.ModelSerializer):
    total_businesses = serializers.IntegerField(read_only=True)
    total_users = serializers.IntegerField(read_only=True)
    total_events = serializers.IntegerField(read_only=True)
    total_promotions = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Municipality
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'updated_at']
