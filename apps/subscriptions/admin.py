from django.contrib import admin
from .models import Plan, Subscription
from shared.admin import TenantAdminMixin

@admin.register(Plan)
class PlanAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'price_period', 'is_active', 'is_featured']
    list_filter = ['plan_type', 'is_active', 'is_featured']
    search_fields = ['name', 'description']

@admin.register(Subscription)
class SubscriptionAdmin(TenantAdminMixin, admin.ModelAdmin):
    tenant_filter_path = 'business__municipality'
    list_display = ['business', 'plan', 'status', 'start_date', 'end_date', 'auto_renew']
    list_filter = ['status', 'plan', 'auto_renew']
    search_fields = ['business__name']
    readonly_fields = ['created_at', 'updated_at']
