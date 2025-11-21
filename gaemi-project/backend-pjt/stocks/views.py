from rest_framework import generics # ListAPIView: 단순 조회 업무를 위한 자동화된 로봇
from .models import StockMaster
from .serializers import StockMasterSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

# 주식 목록 조회 전용 뷰 (GET)
class StockListView(generics.ListAPIView):
    # 1. 어떤 데이터를 보여줄 건지? -> StockMaster의 모든 데이터
    queryset = StockMaster.objects.all()

    # 2. 어떤 방식으로 직렬화 할지
    serializer_class = StockMasterSerializer

    # 3. 누구에게 보여줄건지 -> 로그인한 사람에게만
    permission_classes = [AllowAny] # 모두에게 보여주려면 AllowAny으로 바꾸면 됨!