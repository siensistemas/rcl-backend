from django.contrib import admin
from .models import Municipality

@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'is_public', 'total_businesses', 'created_at']
    list_filter = ['is_active', 'is_public', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Informacion Basica', {
            'fields': ('name', 'slug', 'description', 'slogan')
        }),
        ('Branding', {
            'fields': ('logo', 'favicon', 'banner', 'primary_color', 'secondary_color', 
                      'accent_color', 'background_color', 'primary_font', 'secondary_font')
        }),
        ('Contacto', {
            'fields': ('phone', 'email', 'address', 'website')
        }),
        ('Redes Sociales', {
            'fields': ('facebook', 'instagram', 'twitter', 'youtube', 'tiktok')
        }),
        ('Ubicacion', {
            'fields': ('latitude', 'longitude', 'timezone')
        }),
        ('Configuracion', {
            'fields': ('config', 'is_active', 'is_public')
        }),
        ('Suscripcion', {
            'fields': ('subscription_plan', 'subscription_expires_at')
        }),
        ('Estadisticas', {
            'fields': ('views_count', 'created_at', 'updated_at')
        }),
    )
