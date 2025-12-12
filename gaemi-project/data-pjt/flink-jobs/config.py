# data-pjt/flink-jobs/config.py
# # 설정 관리: config.py

import os

# Kafka 설정
KAFKA_BROKER = "kafka:29092"
TOPIC_NEWS_RAW = "news-raw"
GROUP_ID = "flink-news-rag-group"

# ElasticSearch 설정
ES_HOST = "http://elasticsearch:9200"
INDEX_NEWS_SUMMARY = "news-summary"

# OpenAI 설정 (.env 파일로 주입 받기)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 배치 처리 설정
BATCH_WINDOW_SECONDS = 5  # 5초마다 모아서 처리 (수정 가능)
BATCH_SIZE_THRESHOLD = 10 # 10개 모이면 처리 (수정 가능)

# .env에 있는 값 불러오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
OPENAI_MODEL = os.getenv("OPENAI_MODEL")