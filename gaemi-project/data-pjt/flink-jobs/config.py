# data-pjt/flink-jobs/config.py
# 설정 관리: config.py

import os

# Kafka 설정
KAFKA_BROKER = "kafka:29092"
TOPIC_NEWS_RAW = "news-raw"
TOPIC_STOCK_TICKS = "stock-ticks"
TOPIC_ALERT = "alert"  # 알림 전송용 토픽
GROUP_ID = "flink-news-rag-group"
GROUP_ID_NOTIFICATION = "flink-notification-group"

# ElasticSearch 설정
ES_HOST = "http://elasticsearch:9200"
INDEX_NEWS_SUMMARY = "news-summary"
INDEX_STOCK_RAWS = "stock-raws"  

# OpenAI 설정 (.env 파일로 주입 받기)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

# PostgreSQL 설정
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "gaemi_ai")
POSTGRES_USER = os.getenv("POSTGRES_USER", "gaemi")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "gaemigaemi11")

# PostgreSQL 연결 URL
POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# 배치 처리 설정
BATCH_WINDOW_SECONDS = 5  # 5초마다 모아서 처리 (수정 가능)
BATCH_SIZE_THRESHOLD = 10 # 10개 모이면 처리 (수정 가능)

# 알림 설정
RULE_RELOAD_INTERVAL_SECONDS = 60  # 1분마다 규칙 재로딩
ALERT_COOLDOWN_SECONDS = 300  # 5분 쿨타임 (같은 규칙 중복 방지)