import os

# KIS API 설정 (환경변수에서 로드)
KIS_APP_KEY = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET")

KIS_BASE_URL = "https://openapi.koreainvestment.com:9443"
KIS_WS_URL = "ws://ops.koreainvestment.com:21000"

# Kafka 설정 (Docker 내부 통신용 주소)
# docker-compose에서 kafka 서비스의 내부 포트는 29092로 설정함
KAFKA_BROKER = "kafka:29092"
KAFKA_TOPIC_TICKS = "stock-ticks"