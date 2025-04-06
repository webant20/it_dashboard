from django.contrib import admin
from .models import ContractNotification, SMTPSettings, NotificationLog

# Register your models here.

@admin.register(SMTPSettings)
class SMTPSettingsAdmin(admin.ModelAdmin):
    list_display = ('smtp_server', 'smtp_port', 'smtp_username', 'use_tls', 'use_ssl')
    search_fields = ('smtp_server', 'smtp_username')

@admin.register(ContractNotification)
class ContractNotificationAdmin(admin.ModelAdmin):
    list_display = ('contract', 'email_ids', 'days_before_expiry')
    search_fields = ('contract__contract_number', 'email_ids')

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'email', 'sent_at')
    # list_filter = ('notification_type', 'timestamp')
    # search_fields = ('email', 'notification_type')
