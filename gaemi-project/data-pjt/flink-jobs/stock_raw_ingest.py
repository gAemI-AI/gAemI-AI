from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import WatermarkStrategy

import json
import requests


def save_to_elasticsearch(record):
    ES_URL = "http://elasticsearch:9200/raw-stocks/_doc/"

    try:
        res = requests.post(ES_URL, json=record, timeout=5)
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

        for f in required_fields:
            if f not in data:
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

    # # 꼭 필요
    # env.add_jars(
    #     "file:///opt/flink/lib/flink-connector-kafka-1.17.1.jar",
    #     "file:///opt/flink/lib/kafka-clients-3.5.1.jar"
    # )

    # ⭐⭐ 여기 두 줄이 핵심 ⭐⭐
    source = (
        KafkaSource.builder()
        .set_bootstrap_servers("kafka:29092")
        .set_topics("stock-ticks")                       # ← topic 정확히 이 이름
        .set_group_id("flink-stock-consumer-debug-1")    # ← 새 group id
        .set_starting_offsets(KafkaOffsetsInitializer.earliest())  # ← 토픽 처음부터
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    stream = env.from_source(
        source,
        WatermarkStrategy.no_watermarks(),
        "KafkaSource"
    )

    parsed = stream.map(parse_json)
    cleaned = parsed.filter(lambda x: x is not None)

    cleaned.map(save_to_elasticsearch)

    env.execute("StockRawIngestJob")


if __name__ == "__main__":
    run()
