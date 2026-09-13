from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'promotion', 'user', 'status', 'redeemed_at']
    list_filter = ['status']
    search_fields = ['code']