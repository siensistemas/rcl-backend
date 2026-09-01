from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from shared.tenant import resolve_tenant_for_user
from shared.admin import TenantAdminMixin

@admin.register(User)
class CustomUserAdmin(TenantAdminMixin, UserAdmin):
    tenant_filter_path = 'municipality'
    list_display = ['username', 'email', 'role', 'municipality', 'is_verified', 'is_active', 'login_count']
    list_filter = ['role', 'municipality', 'is_verified', 'is_active', 'email_verified', 'phone_verified']
    fieldsets = UserAdmin.fieldsets + (
        ('Informacion Personal', {
            'fields': ('phone', 'avatar', 'cover', 'birth_date', 'gender', 'bio', 'location')
        }),
        ('Roles y Permisos', {
            'fields': ('role', 'municipality', 'is_verified', 'email_verified', 'phone_verified')
        }),
        ('Redes Sociales', {
            'fields': ('facebook', 'instagram', 'twitter', 'linkedin')
        }),
        ('Preferencias', {
            'fields': ('language', 'theme', 'notification_preferences')
        }),
        ('Seguridad', {
            'fields': ('two_factor_enabled', 'two_factor_secret')
        }),
        ('Estadisticas', {
            'fields': ('login_count', 'last_login_ip', 'last_login_device')
        }),
    )
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name']
