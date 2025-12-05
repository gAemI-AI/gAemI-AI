# stock_raw_ingest.py
# Kafka → Flink → Elasticsearch (raw-stocks 저장)

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream import TimeCharacteristic

import json
import requests


# -----------------------------
# 🔧 Elasticsearch Sink 함수
# -----------------------------
def save_to_elasticsearch(record):
    """
    Kafka에서 읽은 데이터(JSON)를 Elasticsearch로 저장한다.
    record는 Python dict 형태이다.
    """
    ES_URL = "http://elasticsearch:9200/raw-stocks/_doc/"

    try:
        res = requests.post(ES_URL, json=record, timeout=5)
        print(f"[ES INSERT] status={res.status_code}, body={record}")

    except Exception as e:
        print(f"[ES ERROR] {e}, record={record}")


# -----------------------------
# 🔧 JSON 파싱 함수
# -----------------------------
def parse_json(value):
    """
    Kafka 메시지(JSON 문자열)를 dict로 변환.
    잘못된 데이터가 들어올 경우를 대비해 예외처리 포함.
    """
    try:
        data = json.loads(value)

        # 필요한 필드만 검증 (명세 기반)
        required_fields = [
            "stock_code", "stock_name", "timestamp", "current_price",
            "diff", "rate", "open_price", "high_price", "low_price",
            "tick_volume", "accumulated_vol"
        ]

        for f in required_fields:
            if f not in data:
                print(f"[WARN] Missing field: {f}")
                data[f] = None  # 기본값

        return data

    except Exception as e:
        print(f"[JSON ERROR] {e}, raw={value}")
        return None


# -----------------------------
# 🚀 Flink Job 실행 함수
# -----------------------------
def run():
    env = StreamExecutionEnvironment.get_execution_environment()

    # Kafka Consumer 설정
    kafka_props = {
        "bootstrap.servers": "kafka:29092",
        "group.id": "flink-stock-consumer",
        "auto.offset.reset": "latest"
    }

    consumer = FlinkKafkaConsumer(
        topics="stock-ticks",
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )

    # Kafka Source 추가
    stream = env.add_source(consumer)

    # JSON → dict 변환
    parsed = stream.map(
        lambda s: parse_json(s),
        output_type=Types.PICKLED_BYTE_ARRAY()
    )

    # None 제거
    cleaned = parsed.filter(lambda x: x is not None)

    # Elasticsearch 저장
    cleaned.map(
        lambda record: save_to_elasticsearch(record),
        output_type=Types.STRING()
    )

    # Job 이름
    env.execute("StockRawIngestJob")


if __name__ == "__main__":
    run()

