from django.urls import path
from .views import StockNewsListView

urlpatterns = [
    path('<str:stock_code>/', StockNewsListView.as_view(), name='stock-news-list'),
]