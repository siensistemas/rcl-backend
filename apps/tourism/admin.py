from django.contrib import admin
from .models import Attraction, TouristRoute

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ['name', 'attraction_type', 'status', 'is_featured']
    list_filter = ['attraction_type', 'status', 'is_featured']
    search_fields = ['name', 'description', 'address']

@admin.register(TouristRoute)
class TouristRouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_text', 'is_featured']
    list_filter = ['is_featured']
    search_fields = ['name', 'description']