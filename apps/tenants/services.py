from django.db import transaction
from django.utils import timezone
from .models import Municipality
from .serializers import MunicipalitySerializer

class MunicipalityService:
    @staticmethod
    def create_municipality(data):
        with transaction.atomic():
            serializer = MunicipalitySerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return serializer.save()
    
    @staticmethod
    def update_municipality(municipality_id, data):
        with transaction.atomic():
            municipality = Municipality.objects.get(id=municipality_id)
            serializer = MunicipalitySerializer(municipality, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            return serializer.save()
    
    @staticmethod
    def deactivate_municipality(municipality_id):
        with transaction.atomic():
            municipality = Municipality.objects.get(id=municipality_id)
            municipality.is_active = False
            municipality.save()
            return municipality
    
    @staticmethod
    def increment_views(municipality_id):
        with transaction.atomic():
            municipality = Municipality.objects.get(id=municipality_id)
            municipality.views_count += 1
            municipality.save()
            return municipality
