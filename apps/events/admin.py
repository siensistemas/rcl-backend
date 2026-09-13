from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'event_type', 'is_featured']
    search_fields = ['title', 'description', 'location']