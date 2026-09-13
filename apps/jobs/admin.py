from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'business', 'job_type', 'work_mode', 'status']
    list_filter = ['job_type', 'work_mode', 'status', 'is_featured']
    search_fields = ['title', 'description']