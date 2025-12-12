# data-pjt/flink-jobs/utils/es_connector.py
# requests 방식을 재사용하여 안정성 확보

import requests
from config import ES_HOST, INDEX_NEWS_SUMMARY

def save_news_to_es(record):
    """
    임베딩된 뉴스 데이터를 ES에 저장하는 함수
    """
    url = f"{ES_HOST}/{INDEX_NEWS_SUMMARY}/_doc/{record['news_id']}"
    
    try:
        # 멱등성을 위해 POST 대신 PUT 사용 (ID 지정) (UPSERT)
        # POST를 사용하면 요청할 때마다 새로운 리소스가 생길 수 있음 (PUT은 덮어씌워 결과가 동일)
        # 중복 문서를 생기지 않게 하기 위해 record['news_id']를 문서 ID로 사용
        res = requests.put(url, json=record, timeout=5)
        
        if res.status_code in [200, 201]: # 201: created / 200: ok
            print(f"💾 [ES Saved] {record['title'][:10]}...")
        else: # 성공 메시지를 받지 않으면 
            print(f"⚠️ [ES Fail] {res.status_code} - {res.text}")
            
    except Exception as e:
        print(f"❌ [ES Error] {e}")
        
    return record