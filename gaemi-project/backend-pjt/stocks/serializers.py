# 프론트가 이해할 수 있는 JSON 형식으로 변경
from rest_framework import serializers
from .models import StockMaster, WeeklyReport

class StockMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMaster
        # 클라이언트에게 보여줄 필드만 선택
        fields = '__all__' # stock_id, stock_name, market_type

# 주간 리포트 용
class WeeklyReportSerializer(serializers.ModelSerializer):
    # StockMaster의 정보를 함께 보여주기 위해 Nested Serializer 사용
    # read_only=True: 리포트 생성은 Spark가 하므로 API로는 읽기만 가능
    stock_name = serializers.CharField(source='stock.stock_name', read_only=True)
    stock_code = serializers.CharField(source='stock.stock_id', read_only=True)

    class Meta:
        model = WeeklyReport
        fields = [
            'id', 
            'stock_code', 
            'stock_name', 
            'start_date', 
            'end_date', 
            'weekly_return', 
            'weekly_high', 
            'weekly_low', 
            'start_price', 
            'end_price', 
            'summary_text', 
            'created_at'
        ]