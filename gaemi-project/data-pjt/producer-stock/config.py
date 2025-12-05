import os

# KIS API 설정  
KIS_APP_KEY = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET")

KIS_BASE_URL = "https://openapi.koreainvestment.com:9443"
KIS_WS_URL = "ws://ops.koreainvestment.com:21000"

# Kafka 설정 (Docker 내부 통신용 주소)
# docker-compose에서 kafka 서비스의 내부 포트는 29092로 설정함
KAFKA_BROKER = "kafka:29092"

# 토픽 정의
KAFKA_TOPIC_TICKS = "stock-ticks"           # 실시간 체결가
KAFKA_TOPIC_ORDERBOOK = "stock-orderbook"   # 실시간 호가
KAFKA_TOPIC_INDEX = "index-ticks"           # 시장 지수