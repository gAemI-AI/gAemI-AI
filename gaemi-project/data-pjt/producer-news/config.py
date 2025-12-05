# data-pjt/producer-news/config.py
import os

# Kafka 설정
KAFKA_BROKER = "gaemi_kafka:29092"
KAFKA_TOPIC_NEWS = "news-raw"

# 구글 뉴스 RSS URL 포맷 / 
# {}: keyword는 종목명(한글)로 추가
RSS_URL_FORMAT = "https://news.google.com/rss/search?q={}&hl=ko&gl=KR&ceid=KR:ko"

# 수집 주기 (초)
CRAWL_INTERVAL = 60