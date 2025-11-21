from django.urls import path
from .views import WatchlistListCreateView, WatchlistDestroyView

urlpatterns = [
    # GET, POST /api/v1/watchlist/
    path('', WatchlistListCreateView.as_view(), name='watchlist-list-create'),
    
    # DELETE /api/v1/watchlist/{stock_id}/
    # 예: /api/v1/watchlist/005930/ (삼성전자 삭제)
    path('<str:stock_id>/', WatchlistDestroyView.as_view(), name='watchlist-delete'),
]