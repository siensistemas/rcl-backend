from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()
    municipality_name = serializers.SerializerMethodField()
    salary_text = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['views_count', 'applications_count', 'created_at', 'updated_at']

    def get_business_name(self, obj):
        return obj.business.name if obj.business else None

    def get_municipality_name(self, obj):
        return obj.municipality.name if obj.municipality else None

    def get_salary_text(self, obj):
        if obj.salary_min is None and obj.salary_max is None:
            return None
        if obj.salary_min and obj.salary_max:
            return f"${obj.salary_min} - ${obj.salary_max}"
        return f"${obj.salary_min or obj.salary_max}"

    def get_is_active(self, obj):
        return obj.status == 'published'