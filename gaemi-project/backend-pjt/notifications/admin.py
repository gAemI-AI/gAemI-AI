# backend-pjt/notifications/admin.py
from django.contrib import admin
from .models import NotificationRule, TriggeredNotification

@admin.register(NotificationRule)
class NotificationRuleAdmin(admin.ModelAdmin):
    list_display = ('rule_id', 'user', 'stock', 'metric_type', 'operator', 'target_value', 'is_active')
    list_filter = ('is_active', 'metric_type')

@admin.register(TriggeredNotification)
class TriggeredNotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_id', 'user', 'stock_name', 'message', 'is_read', 'triggered_at')
    readonly_fields = ('triggered_at',) # 발생 시각은 수정 못하게