# gaemi-project > backend-pjt > news > service.py
# View(요청/응답만)가 더러워지는 것 막기 위해 ES 통신 로직은 Service 계층으로 분리

from elasticsearch import Elasticsearch
from django.conf import settings

class NewsService:
    def __init__(self):
        self.es = Elasticsearch(["http://elasticsearch:9200"])
        self.index_name = "news-summary"

    def get_news_by_stock_code(self, stock_code, limit=3):
        """
        특정 종목의 최신 뉴스 조회 (요약 포함)
        """
        query = {
            "size": limit,  # 현재는 3개 제한
            "sort": [
                {"published_at": {"order": "desc"}}  # 최신순 정렬
            ],
            "_source": ["title", "link", "summary", "sentiment", "published_at", "source"], # 필요한 필드만 가져오기
            "query": {
                "term": {
                    "stock_code": stock_code  # 정확히 일치하는 종목 코드 검색
                }
            }
        }

        try:
            response = self.es.search(index=self.index_name, body=query)
            hits = response['hits']['hits']
            
            # 프론트엔드가 쓰기 편하게 데이터 가공
            news_list = []
            for hit in hits:
                source = hit['_source']
                news_list.append({
                    "id": hit['_id'],
                    "title": source.get('title', ''),
                    "link": source.get('link', ''),
                    "summary": source.get('summary', []), # 3줄 요약 리스트
                    "sentiment": source.get('sentiment', 'NEUTRAL'), # 감성
                    "published_at": source.get('published_at', 0),
                    "source": source.get('source', '뉴스')
                })
            
            return news_list

        except Exception as e:
            print(f"❌ ES Search Error: {e}")
            return []