from django.contrib import admin
from .models import ConsentRecord, RightsRequest, DataExportRequest, AccountDeletionRequest


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'purpose', 'granted', 'consent_version', 'mechanism', 'timestamp']
    list_filter = ['purpose', 'granted', 'mechanism']
    search_fields = ['user__username', 'user__email']


@admin.register(RightsRequest)
class RightsRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'right', 'status', 'created_at']
    list_filter = ['right', 'status']
    search_fields = ['user__username', 'user__email']


@admin.register(DataExportRequest)
class DataExportRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'requested_at']
    list_filter = ['status']
    search_fields = ['user__username', 'user__email']


@admin.register(AccountDeletionRequest)
class AccountDeletionRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'requested_at', 'scheduled_date']
    list_filter = ['status']
    search_fields = ['user__username', 'user__email']