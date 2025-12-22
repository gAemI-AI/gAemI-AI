# backend-pjt/stocks/services.py
from elasticsearch import Elasticsearch
from .utils import get_chosung

class StockSearchService:
    def __init__(self):
        self.es = Elasticsearch(["http://elasticsearch:9200"])
        self.index_name = "stock-search"

    def search(self, keyword):
        if not keyword:
            return []

        # 사용자 입력을 소문자로 변환 (검색 정확도 향상)
        keyword_lower = keyword.lower()
        
        # 사용자 입력의 초성 변환 (ㅎㅇㄴㅅ 검색 지원용)
        keyword_chosung = get_chosung(keyword)

        query = {
            "size": 50,
            "query": {
                "bool": {
                    "should": [
                        # 1. 종목코드 정확 일치 (가장 강력)
                        { "term": { "stock_id": { "value": keyword, "boost": 100 } } },
                        
                        # 2. 종목명 정확/부분 일치 (대소문자 무시됨)
                        { "match_phrase": { "stock_name": { "query": keyword, "boost": 50 } } },
                        { "match": { "stock_name": { "query": keyword, "boost": 10 } } },
                        
                        # 3. [NEW] 동의어 검색 (네이버 -> NAVER 찾기)
                        { "match": { "stock_synonyms": { "query": keyword, "boost": 40 } } },

                        # 4. [NEW] 초성 검색 (skㅎㅇㄴㅅ)
                        # 입력값이 "ㅎㅇㄴㅅ"이면 -> "*ㅎㅇㄴㅅ*" 패턴으로 skㅎㅇㄴㅅ를 찾음
                        { "wildcard": { "stock_name_chosung": { "value": f"*{keyword_chosung}*", "boost": 5 } } },
                        
                        # 5. 오타 보정
                        { "match": { "stock_name": { "query": keyword, "fuzziness": "AUTO", "boost": 1 } } }
                    ],
                    "minimum_should_match": 1
                }
            }
        }

        try:
            response = self.es.search(index=self.index_name, body=query)
            hits = response['hits']['hits']
            
            # Serializer와 유사한 형태로 데이터 반환
            results = []
            for hit in hits:
                source = hit['_source']
                results.append({
                    "stock_id": source.get('stock_id'),
                    "stock_name": source.get('stock_name'),
                    "market_type": source.get('market_type')
                })
            return results
        
        except Exception as e:
            print(f"ES Search Error: {e}")
            return []