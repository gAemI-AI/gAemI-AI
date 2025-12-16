from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import WatermarkStrategy

import json
import requests
import time


def save_to_elasticsearch(record):
    ES_URL = "http://elasticsearch:9200/raw-stocks/_doc/"

    try:
        res = requests.post(ES_URL, json=record, timeout=5) #post: 같은 종목이라도 시간이 다르면 새 데이터 -> 계속 쌓여야하므로 ID 자동 생성 POST 사용
        print(f"[ES INSERT] {res.status_code} {record}")
    except Exception as e:
        print(f"[ES ERROR] {e}, record={record}")

    return record


def parse_json(value: str):
    print("🔥 RAW:", value)

    try:
        data = json.loads(value)

        required_fields = [
            "stock_code", "stock_name", "timestamp", "current_price",
            "diff", "rate", "open_price", "high_price", "low_price",
            "tick_volume", "accumulated_vol"
        ]

        # 필수 데이터(종목코드, 현재가 등)가 있는지 검사
        for f in required_fields:
            if f not in data: # 없으면 None으로 채워 데이터 형식 맞춤
                print(f"[WARN] Missing field: {f}")
                data[f] = None

        print("✅ Parsed:", data)
        return data

    except Exception as e:
        print(f"[JSON ERROR] {e}, raw={value}")
        return None


def run():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    # Kafka 연결 재시도 로직
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"[KAFKA] 연결 시도 {attempt + 1}/{max_retries}")
            source = (
                KafkaSource.builder()
                .set_bootstrap_servers("kafka:29092")
                .set_topics("stock-ticks")                       # ← topic 정확히 이 이름
                .set_group_id("flink-stock-consumer-debug-1")    # ← 새 group id
                .set_starting_offsets(KafkaOffsetsInitializer.earliest())  # ← 토픽 처음부터
                .set_value_only_deserializer(SimpleStringSchema())
                .build()
            )
            print("[KAFKA] ✅ 연결 성공")
            break
        except Exception as e:
            print(f"[KAFKA] ❌ 연결 실패: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise

    stream = env.from_source(
        source,
        WatermarkStrategy.no_watermarks(),
        "KafkaSource"
    )

    parsed = stream.map(parse_json) # 카프카에서 받은 문자열 JSON으로 변환
    cleaned = parsed.filter(lambda x: x is not None) # JSON 변환에 실패한 데이터(None)는 stream에서 제거

    cleaned.map(save_to_elasticsearch) 

    env.execute("StockRawIngestJob")


if __name__ == "__main__":
    run()
