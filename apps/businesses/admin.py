from django.contrib import admin
from .models import Business, BusinessMedia, BusinessHours
from shared.admin import TenantAdminMixin

class BusinessMediaInline(admin.TabularInline):
    model = BusinessMedia
    extra = 1

class BusinessHoursInline(admin.TabularInline):
    model = BusinessHours
    extra = 7

@admin.register(Business)
class BusinessAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'slug', 'municipality', 'category', 'owner', 'is_verified', 'is_active', 'views_count']
    list_filter = ['municipality', 'category', 'is_verified', 'is_active', 'is_featured']
    search_fields = ['name', 'slug', 'description', 'address']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [BusinessMediaInline, BusinessHoursInline]
    readonly_fields = ['views_count', 'clicks_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Informacion Basica', {
            'fields': ('name', 'slug', 'short_name', 'description', 'history', 'mission', 'vision', 'values')
        }),
        ('Ubicacion', {
            'fields': ('address', 'neighborhood', 'city', 'state', 'zip_code', 'latitude', 'longitude')
        }),
        ('Contacto', {
            'fields': ('phone', 'whatsapp', 'email', 'website')
        }),
        ('Redes Sociales', {
            'fields': ('facebook', 'instagram', 'tiktok', 'youtube', 'twitter', 'linkedin', 'pinterest')
        }),
        ('Categorizacion', {
            'fields': ('municipality', 'category', 'subcategory')
        }),
        ('Verificacion', {
            'fields': ('is_verified', 'verification_date', 'verified_by')
        }),
        ('Estado', {
            'fields': ('is_active', 'is_featured', 'is_approved', 'approval_date')
        }),
        ('Plan', {
            'fields': ('plan', 'plan_expires_at', 'plan_auto_renew')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Estadisticas', {
            'fields': ('views_count', 'clicks_count', 'whatsapp_clicks', 'call_clicks', 
                      'direction_clicks', 'website_clicks', 'social_clicks', 
                      'favorite_count', 'share_count')
        }),
    )

@admin.register(BusinessMedia)
class BusinessMediaAdmin(TenantAdminMixin, admin.ModelAdmin):
    tenant_filter_path = 'business__municipality'
    list_display = ['business', 'media_type', 'title', 'is_cover', 'is_featured', 'views_count']
    list_filter = ['media_type', 'is_cover', 'is_featured']
    search_fields = ['title', 'description']

@admin.register(BusinessHours)
class BusinessHoursAdmin(TenantAdminMixin, admin.ModelAdmin):
    tenant_filter_path = 'business__municipality'
    list_display = ['business', 'day', 'open_time', 'close_time', 'is_closed']
    list_filter = ['day', 'is_closed']
