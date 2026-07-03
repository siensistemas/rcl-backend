from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    total_businesses = serializers.IntegerField(read_only=True)
    depth = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data
