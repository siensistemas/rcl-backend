from django.contrib import admin
from .models import Ad

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['title', 'ad_type', 'placement', 'status', 'start_date', 'end_date']
    list_filter = ['ad_type', 'placement', 'status']
    search_fields = ['title', 'description']