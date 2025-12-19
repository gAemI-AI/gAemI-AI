from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Watchlist
from .serializers import WatchlistSerializer
from django.shortcuts import get_object_or_404
from elasticsearch import Elasticsearch

# 1. 목록 조회(GET) 및 추가(POST)
class WatchlistListCreateView(generics.ListCreateAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated] # 로그인 필수

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ES 연결 설정
        self.es = Elasticsearch(
            hosts=[{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}]
        )

    # 로그인한 유저의 데이터만 가져옴 (User Isolation)
    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).order_by('-created_at')
    
    # user 필드는 로그인한 사람으로 자동 채움
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # 목록 조회 시 '현재가' 주입하기
    def list(self, request, *args, **kwargs):
        # 1. DB에서 내 관심 종목 리스트 가져오기
        response = super().list(request, *args, **kwargs)
        watchlist_data = response.data 

        if not watchlist_data:
            return response

        # 2. 종목 코드 리스트 추출
        stock_codes = [item['stock'] for item in watchlist_data]

        # 3. Elasticsearch에서 최신 가격 조회 (Terms Aggregation)
        try:
            es_query = {
                "size": 0, # 문서 자체는 필요 없음
                "query": {
                    "bool": {
                        "filter": [
                            {"terms": {"stock_code": stock_codes}} # 내 종목들만 필터링
                        ]
                    }
                },
                "aggs": {
                    "by_stock": {
                        "terms": {"field": "stock_code.keyword", "size": 100},  # stock_code 기준으로 bucket 생성 (최대 100 종목까지만 가능하도록 설정)
                        "aggs": {
                            "latest_price": {
                                "top_hits": { # 각 bucket 안에서 실제 문서를 다시 가져오는 집계(가장 최신 것만 가져오기 위해)
                                    "sort": [{"timestamp": "desc"}], # 최신순
                                    "_source": ["current_price", "diff", "rate"],  # 필요한 필드만 선택
                                    "size": 1 # 현재가 최신 1건만 필요
                                }
                            }
                        }
                    }
                }
            }

            es_res = self.es.search(index="raw-stocks", body=es_query)
            buckets = es_res['aggregations']['by_stock']['buckets']

            # 4. 가격 데이터 매핑 (Dictionary 변환)
            price_map = {}
            for bucket in buckets:
                code = bucket['key']
                hits = bucket['latest_price']['hits']['hits']
                if hits:
                    source = hits[0]['_source']
                    price_map[code] = {
                        "current_price": source.get('current_price', 0),
                        "diff": source.get('diff', 0),
                        "rate": source.get('rate', 0.0)
                    }

            # 5. 기존 응답 데이터에 가격 정보 합치기
            for item in watchlist_data:
                code = item['stock']
                # ES에서 가져온 가격 정보가 있으면 병합, 없으면 0 처리
                price_info = price_map.get(code, {"current_price": 0, "diff": 0, "rate": 0.0})
                item.update(price_info)

            return Response(watchlist_data)

        except Exception as e:
            print(f"Watchlist Price Error: {e}")
            # 에러가 나더라도 목록은 보여줘야 함 (가격은 0으로)
            return response

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

