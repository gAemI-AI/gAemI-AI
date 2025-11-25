# 읽을 때(get)는 종목정보 자세히 보여줌 
# 쓸 때 (post)는 종목 ID만 받는 방식

from rest_framework import serializers
from .models import NotificationRule
from stocks.serializers import StockMasterSerializer

class NotificationRuleSerializer(serializers.ModelSerializer):
    # 읽기 전용: 종목 상세 정보 포함
    stock_details = StockMasterSerializer(source='stock', read_only=True)

    class Meta:
        model = NotificationRule
        fields = [
            'rule_id',
            'stock',
            'stock_details',
            'metric_type',
            'operator', 
            'target_value', 
            'is_active'
        ]
        read_only_fields = ['user'] # 유저는 서버가 자동 입력