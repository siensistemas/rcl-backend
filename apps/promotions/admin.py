from django.contrib import admin
from .models import Promotion

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'business', 'discount_type', 'discount_value', 'status', 'start_date', 'end_date', 'is_valid']
    list_filter = ['status', 'discount_type', 'is_featured', 'business']
    search_fields = ['title', 'description', 'subtitle']
    readonly_fields = ['views_count', 'redeemed_count', 'clicks_count', 'share_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Informacion Basica', {
            'fields': ('business', 'title', 'subtitle', 'description')
        }),
        ('Media', {
            'fields': ('image', 'video', 'gallery')
        }),
        ('Vigencia', {
            'fields': ('start_date', 'end_date')
        }),
        ('Condiciones', {
            'fields': ('conditions', 'terms')
        }),
        ('Cantidad', {
            'fields': ('available_quantity', 'used_quantity', 'max_per_user', 'is_unlimited')
        }),
        ('Descuento', {
            'fields': ('discount_type', 'discount_value', 'min_purchase', 'max_discount')
        }),
        ('Estado', {
            'fields': ('status', 'is_featured')
        }),
        ('Estadisticas', {
            'fields': ('views_count', 'redeemed_count', 'clicks_count', 'share_count')
        }),
    )
