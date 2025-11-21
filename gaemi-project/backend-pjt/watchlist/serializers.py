from rest_framework import serializers
from .models import Watchlist
from stocks.serializers import StockMasterSerializer # stocks 앱의 번역기 재사용

class WatchlistSerializer(serializers.ModelSerializer):
    # stock 정보 자세히 보여주기 위해 중첩 사용
    stock_details = StockMasterSerializer(source='stock', read_only=True)

    class Meta:
        model = Watchlist
        # stock: 입력용 (ID만 받음)
        # stock_details: 출력용 (이름, 시장구분 등을 자세히 보여줌)
        fields = ['watchlist_id', 'stock', 'stock_details', 'created_at']
        read_only_fields = ['user'] # 유저는 서버가 알아서 넣으므로 입력하지 않음

        # 데이터 넣을 때(POST)는 stock_id만 주면 됨
        # 데이터를 꺼낼 때(GET)는 stock_id만 주면 프론트가 무슨 종목인지 모름
        # 그래서 꺼낼 때(Read)는 종목 이름까지 다 보여주는 중첩 시리얼라이저 사용

        