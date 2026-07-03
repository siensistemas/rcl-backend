from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'municipality', 'parent', 'is_active', 'is_featured', 'order', 'total_businesses']
    list_filter = ['municipality', 'parent', 'is_active', 'is_featured']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
