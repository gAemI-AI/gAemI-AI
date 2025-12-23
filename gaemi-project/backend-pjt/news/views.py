from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import NewsService

class StockNewsListView(APIView):
    """
    특정 종목의 최신 AI 요약 뉴스 조회
    GET /news/{stock_code}/
    """
    def get(self, request, stock_code):
        service = NewsService()
        news_data = service.get_news_by_stock_code(stock_code=stock_code, limit=5)
        
        response_data = {
            "stock_code": stock_code,
            "count": len(news_data),
            "data": news_data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)