# gaemi-project > data-pjt > consumer-index > main.py
# Kafka 토픽(index-ticks)에서 지수 데이터를 실시간 소비 -> Elasticsearch에 index_code 기준으로 최신 값만 Upsert 저장
# 즉, 현재 상태 테이블 형태 저장

import json
import logging
import os
import sys
import time
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch, helpers

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 환경변수 로드
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = os.environ.get("TOPIC_NAME", "index-ticks")
ES_HOST = os.environ.get("ES_HOST", "http://elasticsearch:9200")
ES_INDEX = os.environ.get("ES_INDEX", "index-ticks")

def create_es_index(es):
    """
    Elasticsearch 인덱스 및 매핑 생성 (Consumer 시작 1회 실행)
    - index_code는 집계(Aggregation)를 위해 반드시 'keyword' 타입
    - ES에 해당 인덱스가 없다면 생성
    """
    if not es.indices.exists(index=ES_INDEX):
        mapping = {
            "mappings": {
                "properties": {
                    "index_code": {"type": "keyword"},  # 백엔드 terms 집계용 (text면 집계 불가 !!)
                    "timestamp": {"type": "date"}, # Kibana 시계열 시각화 가능
                    "current_value": {"type": "float"},
                    "change_value": {"type": "float"},
                    "change_rate": {"type": "float"},
                    "volume": {"type": "long"}
                }
            }
        }
        es.indices.create(index=ES_INDEX, body=mapping)
        logger.info(f"인덱스 생성 완료: {ES_INDEX}")

def run_consumer():
    # 1. Kafka Consumer 연결
    logger.info(f"Kafka 연결 시도: {KAFKA_BROKER} (Topic: {TOPIC_NAME})")
    consumer = None
    while not consumer: # Kafka가 늦게 뜨는 상황 대응 (Docker 환경이니까)
        try:
            consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=[KAFKA_BROKER],
                auto_offset_reset='latest', # consumer 시작 이후 데이터만
                enable_auto_commit=True, # 처리 후 offset 자동 커밋
                group_id='index-consumer-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info("Kafka Consumer 연결 성공!")
        except Exception as e:
            logger.warning(f"❌ Kafka 연결 실패 (5초 후 재시도): {e}")
            time.sleep(5)

    # 2. Elasticsearch 연결
    logger.info(f"Elasticsearch 연결 시도: {ES_HOST}")
    es = Elasticsearch([ES_HOST])
    while not es.ping(): # docker 환경을 위한 지연 대응
        logger.warning("❌ ES 연결 실패 (5초 후 재시도)")
        time.sleep(5)
    logger.info("Elasticsearch 연결 성공!")

    # 인덱스 생성
    create_es_index(es)

    # 3. 데이터 처리 루프
    logger.info("Index Consumer 가동 시작...")
    
    # ES Bulk Insert 최적화: 1건씩 넣는 것보다 훨씬 빠름
    actions = []
    BATCH_SIZE = 10 

    for message in consumer:
        try:
            data = message.value
            
            # _id를 index_code로 지정하여 "덮어쓰기(Upsert)" 처리
            # 이렇게 하면 ES에는 항상 '최신 상태'의 문서만 남게 되어 용량과 속도 면에서 유리
            action = {
                "_index": ES_INDEX,
                "_id": data.get("index_code"), 
                "_source": data
            }
            actions.append(action)

            if len(actions) >= BATCH_SIZE:
                helpers.bulk(es, actions)
                logger.info(f"{len(actions)}건 갱신 완료 (Latest: {data.get('index_code')})")
                actions = []

        except Exception as e:
            logger.error(f"❌ 데이터 처리 중 에러: {e}")

    if actions: # 종료시 남은 데이터 처리: Graceful shutdown 대비
        helpers.bulk(es, actions)

if __name__ == "__main__":
    run_consumer()