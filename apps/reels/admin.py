from django.contrib import admin
from .models import Reel

@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ['title', 'business', 'status', 'views_count', 'likes_count']
    list_filter = ['status', 'is_featured']
    search_fields = ['title', 'description']