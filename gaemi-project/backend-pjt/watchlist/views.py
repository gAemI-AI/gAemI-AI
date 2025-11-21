from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Watchlist
from .serializers import WatchlistSerializer
from django.shortcuts import get_object_or_404

# 1. 목록 조회(GET) 및 추가(POST)
class WatchlistListCreateView(generics.ListCreateAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated] # 로그인 필수

    # 로그인한 유저의 데이터만 가져옴 (User Isolation)
    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)
    
    # user 필드는 로그인한 사람으로 자동 채움
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 2. 삭제(Delete) - stock_id 기준 (관심종목에서 주식 삭제 API)
class WatchlistDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WatchlistSerializer

    # 삭제할 때도 역시 '내 것' 안에서만 찾아야 함
    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)
    

    # 보통 watchlist_id로 삭제하는데, stock_id로 삭제 
    # 기본 동작(PK조회)을 덮어쓰고 stock_id로 내 목록에서 찾아서 지움 
    # -> 그럼 프론트는 직관적으로 'stock_id'를 지워야지!가 됨
    # watchlist_id로 삭제하면 -> 한 번 더 조회를 해야함
    def get_object(self):
        # URL에서 'stock_id' 파라미터를 꺼냄
        stock_id_from_url = self.kwargs['stock_id']
        
        # 내 관심 종목 중에서 해당 stock_id를 가진 항목을 찾음 (없으면 404)
        obj = get_object_or_404(
            Watchlist, 
            user=self.request.user, 
            stock_id=stock_id_from_url
        )
        return obj

