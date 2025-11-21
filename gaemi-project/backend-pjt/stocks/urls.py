from django.urls import path
from .views import StockListView

urlpatterns = [
    # GET / api/v1/stocks/ 주소로 요청오면 -> StockListView가 처리
    path('', StockListView.as_view(), name='stock-list'),
]
