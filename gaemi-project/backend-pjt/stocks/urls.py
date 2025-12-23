from django.urls import path
from .views import StockListView
from .views import StockListView, StockChartView # StockChartView 임포트
from .views import StockListView, StockChartView, MarketIndexView 
from .views import StockListView, StockChartView, MarketIndexView, WeeklyReportView

urlpatterns = [
    # GET / api/v1/stocks/ 주소로 요청오면 -> StockListView가 처리
    path('', StockListView.as_view(), name='stock-list'),

    # 차트 데이터 API: (예) /api/v1/stocks/005930/chart/
    path('<str:stock_code>/chart/', StockChartView.as_view(), name='stock_chart'),

    # 시장 지수 API
    path('market-index/', MarketIndexView.as_view(), name='market-index'),

    # 주간 리포트 API
    # URL: /api/v1/stocks/reports/weekly/
    path('reports/weekly/', WeeklyReportView.as_view(), name='weekly-report'),
]
