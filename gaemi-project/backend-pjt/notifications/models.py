from django.db import models
from django.conf import settings
from stocks.models import StockMaster

class NotificationRule(models.Model):
    rule_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stock = models.ForeignKey(StockMaster, on_delete=models.CASCADE)

    # 예: price, sentiment
    metric_type = models.CharField(max_length=20)
    # 예: >=, <=, ==
    operator = models.CharField(max_length=10)
    # 예: 80000, negative
    target_value = models.CharField(max_length=50)

    # 활성화 여부
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_notification_rules'

class TriggeredNotification(models.Model):
    notification_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # 알림 당시의 종목명 (StockMaster가 삭제되어도 기록은 남아야하므로 텍스트로 저장하거나, FK를 SET_NULL로 설정)
    stock_name = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'triggered_notifications'
        ordering = ['-triggered_at'] # 최신순 정렬