from django.contrib import admin
from .models import Classified

@admin.register(Classified)
class ClassifiedAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'condition', 'status']
    list_filter = ['category', 'condition', 'status']
    search_fields = ['title', 'description']