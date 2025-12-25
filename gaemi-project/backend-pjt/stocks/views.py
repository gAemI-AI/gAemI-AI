from rest_framework import generics # ListAPIView: 단순 조회 업무를 위한 자동화된 로봇
from .models import StockMaster
from .serializers import StockMasterSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from elasticsearch import Elasticsearch
from .services import StockSearchService  

# 주식 목록 조회 전용 뷰 (GET)
class StockListView(generics.ListAPIView):
    # 1. 어떤 데이터를 보여줄 건지? -> StockMaster의 모든 데이터
    queryset = StockMaster.objects.all()

    # 2. 어떤 방식으로 직렬화 할지
    serializer_class = StockMasterSerializer

    # 3. 누구에게 보여줄건지 -> 로그인한 사람에게만
    permission_classes = [AllowAny] # 모두에게 보여주려면 AllowAny으로 바꾸면 됨!

    def list(self, request, *args, **kwargs):
        # 검색어 파라미터 가져오기 (?search=삼성)
        keyword = request.query_params.get('search', '').strip()

        # A. 검색어가 있다면 -> Elasticsearch 사용
        if keyword:
            service = StockSearchService()
            es_results = service.search(keyword)
            
            # ES 결과를 그대로 반환 (Serializer를 거치지 않고 직접 리스트 반환)
            # RDB 조회 비용 절약 + ES의 빠른 속도 활용
            return Response(es_results, status=status.HTTP_200_OK)

        # B. 검색어가 없다면 -> 기존 RDB Pagination 로직 사용
        return super().list(request, *args, **kwargs)
    
# 주식 차트 데이터 조회 API (OHLC Aggregation)
#   - ES의 주식 틱 데이터를 조회하여 지정된 시간 간격으로 집계한 캔들 데이터를 반환
#   - URL: GET /api/v1/stocks/{stock_code}/chart/?range=1d&interval=1m
class StockChartView(APIView):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.es = Elasticsearch(
            hosts=[{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}]
        )

    def get(self, request, stock_code):
        # 1. 파라미터 파싱
        search_range = request.query_params.get('range', '1d')   
        interval = request.query_params.get('interval', '1m')    

        # 2. 조회 기간 계산 (ISO String 형식으로 변환)
        now = datetime.now()
        start_time = now - timedelta(days=1) 
        
        if search_range == '1d':
            start_time = now - timedelta(days=1)
        elif search_range == '1w':
            start_time = now - timedelta(weeks=1)
        elif search_range == '1M':
            start_time = now - timedelta(days=30)
            
        #  데이터가 "2025-12-16T..." 문자열이므로, 쿼리도 문자열로
        gte_timestamp = start_time.isoformat() 

        # 3. ES 집계 쿼리 작성
        query_body = {
            "size": 0,  # 개별 문서는 가져오지 않음 (집계만)
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"stock_code": stock_code}}, 
                        # range 쿼리에 ISO 문자열 사용
                        {"range": {"timestamp": {"gte": gte_timestamp}}} 
                    ]
                }
            },
            "aggs": {
                "candles": {
                    # 캔들 봉 만들기
                    "date_histogram": {
                        "field": "timestamp", # timestamp 기준으로 일정 시간 단위로 묶음
                        "fixed_interval": interval,
                        "time_zone": "+09:00", # 한국 주식 -> KST 기준
                        "min_doc_count": 1 # 이 구간에 문서가 최소 1개 이상 있는 버킷만 만듦 / 없다면? 데이터가 없어도 버킷 생성
                        # 연속된 시간 축을 만들기 위해서는 이게 0 이여야함 
                        # but 우리는 지금 체결 정보 즉 이벤트 기반이므로 거래가 발생했을때만 의미있는 데이터가 생김
                        # 캔들 차트는 시간이 아니라 가격 변화를 보여줌으로 가짜 캔들을 만들면 오히려 정보가 왜곡 될 수 있음
                    },
                    "aggs": {
                        # 고가 / 저가
                        "high": {"max": {"field": "current_price"}}, # 해당 봉에서 가장 비싼 값
                        "low": {"min": {"field": "current_price"}}, # 해당 봉에서 가장 싼 값
                        
                        # 데이터에 tick_volume이 있으면 합산
                        "volume": {"sum": {"field": "tick_volume"}},

                        # 시가 
                        "open_record": {
                            "top_hits": {
                                "sort": [{"timestamp": "asc"}], # 봉 시작 시가나 가장 처음 체결된 가격
                                "_source": ["current_price"], 
                                "size": 1
                            }
                        },
                        # 종가 
                        "close_record": {
                            "top_hits": {
                                "sort": [{"timestamp": "desc"}], # 봉 끝 시간 가장 마지막 체결 가격
                                "_source": ["current_price"], 
                                "size": 1
                            }
                        }
                    }
                }
            }
        }

        try:
            response = self.es.search(index="raw-stocks", body=query_body)
            buckets = response['aggregations']['candles']['buckets'] # 하나의 bucket -> 하나의 봉

            chart_data = []
            for bucket in buckets:
                # 데이터 안전하게 꺼내기 (ES 집계가 비어있을 수 있음)
                open_hits = bucket['open_record']['hits']['hits']
                close_hits = bucket['close_record']['hits']['hits']
                
                if open_hits and close_hits:
                    open_source = open_hits[0]['_source']
                    close_source = close_hits[0]['_source']
                    
                    # 1순위: current_price, 2순위: price, 없으면: 0
                    open_price = open_source.get('current_price', open_source.get('price', 0))
                    close_price = close_source.get('current_price', close_source.get('price', 0))
                    high_price = bucket['high']['value']
                    low_price = bucket['low']['value']
                    volume = bucket['volume']['value']
                    
                    # High/Low가 None일 경우 방어 (혹시 모를 상황 대비) -> 집계가 깨졌더라도 차트는 최소한 그려질 수 있도록 방어
                    if high_price is None: high_price = max(open_price, close_price)
                    if low_price is None: low_price = min(open_price, close_price)

                    # 응답 구조: { x: 시간, y: [시,고,저,종], v: 거래량 }
                    chart_data.append({
                        "x": bucket['key'],  # 시간
                        "y": [open_price, high_price, low_price, close_price], # 가격 [O,H,L,C]
                        "v": int(volume)  # 소수점 제거
                    })

            return Response(chart_data, status=status.HTTP_200_OK) # 차트에 바인딩

        except Exception as e:
            print(f"Chart Error: {e}")
            return Response([], status=status.HTTP_200_OK)
        
# 메인 대시보드용 시장 지수(KOSPI, KOSDAQ 등) 조회 API
class MarketIndexView(APIView):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Docker 내부 통신용 ES 주소
        self.es = Elasticsearch(
            hosts=[{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}]
        )
        
        # 데이터 코드 -> 화면 표시 이름 매핑
        self.INDEX_MAP = {
            "0001": "KOSPI",
            "1001": "KOSDAQ",
            "2001": "KOSPI200"
        }

    def get(self, request):
        # 1. ES Aggregation 쿼리
        # - index_code별로 그룹핑하여 가장 최신(timestamp desc) 데이터 1개만 가져옴
        query_body = {
            "size": 0,
            "aggs": {
                "indices": {
                    # Consumer에서 mapping한 대로 .keyword 필드 사용 필수 -> 삭제
                    "terms": { 
                        "field": "index_code", 
                        "size": 10 # 현재는 3개이지만 확장 대비로 10개
                    },
                    "aggs": {
                        "latest_data": {
                            "top_hits": {
                                "sort": [{"timestamp": "desc"}],
                                "size": 1,
                                "_source": ["index_code", "current_value", "change_value", "change_rate"]
                            }
                        }
                    }
                }
            }
        }

        try:
            # 인덱스가 아직 생성되지 않았을 경우 (Consumer 실행 전) 방어 코드
            if not self.es.indices.exists(index="index-ticks"):
                return Response([], status=status.HTTP_200_OK)

            response = self.es.search(index="index-ticks", body=query_body)
            buckets = response['aggregations']['indices']['buckets']

            result = []
            for bucket in buckets:
                hits = bucket['latest_data']['hits']['hits']
                if hits:
                    source = hits[0]['_source']
                    raw_code = source.get('index_code')
                    
                    # 2. 데이터 변환 (Backend -> Frontend 규격 맞춤)
                    display_name = self.INDEX_MAP.get(raw_code, raw_code) # 매핑 없으면 코드 그대로 출력
                    
                    result.append({
                        "name": display_name,                 # 예: "KOSPI"
                        "price": source.get('current_value'), # 예: 2500.50
                        "diff": source.get('change_value'),   # 예: -15.2
                        "rate": source.get('change_rate')     # 예: -0.6
                    })

            # 3. 화면 표시 순서 정렬 (KOSPI -> KOSDAQ -> 나머지)
            order_priority = {"KOSPI": 1, "KOSDAQ": 2, "KOSPI200": 3}
            result.sort(key=lambda x: order_priority.get(x['name'], 99))

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"🚨 Market Index Error: {e}")
            # 에러 발생 시 500 대신 빈 배열 반환 (프론트엔드 보호)
            return Response([], status=status.HTTP_200_OK)