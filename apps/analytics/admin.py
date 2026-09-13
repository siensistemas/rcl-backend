from django.contrib import admin
from .models import AnalyticEvent

@admin.register(AnalyticEvent)
class AnalyticEventAdmin(admin.ModelAdmin):
    list_display = ['business', 'event_type', 'source', 'created_at']
    list_filter = ['event_type', 'source']
    date_hierarchy = 'created_at'