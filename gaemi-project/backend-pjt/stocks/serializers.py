# 프론트가 이해할 수 있는 JSON 형식으로 변경
from rest_framework import serializers
from .models import StockMaster

class StockMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMaster
        # 클라이언트에게 보여줄 필드만 선택
        fields = '__all__' # stock_id, stock_name, market_type