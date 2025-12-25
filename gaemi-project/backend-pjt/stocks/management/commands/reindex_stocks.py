# backend-pjt/stocks/management/commands/reindex_stocks.py

from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch, helpers
from django.conf import settings
from stocks.models import StockMaster
from stocks.utils import get_chosung

# 동의어 사전 (하드코딩으로 관리 - 필요 시 DB화 가능)
SYNONYM_MAP = {
    "NAVER": "네이버",
    "POSCO홀딩스": "포스코",
    "LG에너지솔루션": "엘지엔솔",
    "SK하이닉스": "하이닉스", # '하이닉스'라고만 쳐도 SK하이닉스가 1순위로 뜨게 보조
}

class Command(BaseCommand):
    help = 'StockMaster 데이터를 강력한 검색 기능을 위해 Elasticsearch로 인덱싱합니다.'

    def handle(self, *args, **options):
        es = Elasticsearch(["http://elasticsearch:9200"])
        index_name = "stock-search"

        # 1. 인덱스 설정 (Lowercase 필터 추가!)
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
            self.stdout.write(self.style.WARNING(f"기존 인덱스 '{index_name}' 삭제됨."))

        settings_body = {
            "settings": {
                "analysis": {
                    "tokenizer": {
                        "ngram_tokenizer": {
                            "type": "edge_ngram",
                            "min_gram": 1,
                            "max_gram": 20,
                            "token_chars": ["letter", "digit", "punctuation", "symbol"] 
                            # punctuation 추가: T.Rowe Price 같은 종목 대비
                        }
                    },
                    "analyzer": {
                        "ngram_analyzer": {
                            "type": "custom",
                            "tokenizer": "ngram_tokenizer",
                            "filter": ["lowercase"] # 👈 핵심: 대소문자 무시 (SAMSUNG == samsung)
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "stock_id": { "type": "keyword" },
                    "stock_name": { 
                        "type": "text", 
                        "analyzer": "ngram_analyzer", 
                        "search_analyzer": "standard" 
                    },
                    # 동의어도 검색되게 별도 필드 생성
                    "stock_synonyms": {
                         "type": "text",
                         "analyzer": "ngram_analyzer",
                         "search_analyzer": "standard"
                    },
                    "stock_name_chosung": { "type": "keyword" }, 
                    "market_type": { "type": "keyword" }
                }
            }
        }
        
        es.indices.create(index=index_name, body=settings_body)
        self.stdout.write(self.style.SUCCESS(f"인덱스 '{index_name}' 생성 완료."))

        # 2. 데이터 가공 및 동의어 주입
        stocks = StockMaster.objects.all()
        actions = []
        
        for stock in stocks:
            # 동의어 찾기
            synonym = SYNONYM_MAP.get(stock.stock_name, "")
            
            # 초성 변환 (SK하이닉스 -> skㅎㅇㄴㅅ)
            chosung = get_chosung(stock.stock_name)
            
            doc = {
                "_index": index_name,
                "_id": stock.stock_id,
                "_source": {
                    "stock_id": stock.stock_id,
                    "stock_name": stock.stock_name,
                    "stock_synonyms": synonym, # "네이버" 등이 들어감
                    "stock_name_chosung": chosung,
                    "market_type": stock.market_type
                }
            }
            actions.append(doc)

        # 3. Bulk Insert
        if actions:
            helpers.bulk(es, actions)
            self.stdout.write(self.style.SUCCESS(f"총 {len(actions)}건 인덱싱 완료!"))