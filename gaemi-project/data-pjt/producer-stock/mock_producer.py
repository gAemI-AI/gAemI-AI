import json
import time
import random
import sys
import os
from datetime import datetime

# config.py 경로 인식을 위해 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import KAFKA_BROKER
TOPIC_STOCK_TICKS = "stock-ticks"

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable


def run_mock_producer():
    print("🚀 [Mock] 가짜 주식 데이터 생성기 시작")
    print(f"👉 Target Kafka: {KAFKA_BROKER}")
    print(f"👉 Target Topic: {TOPIC_STOCK_TICKS}")

    producer = None

    # 1️⃣ Kafka 연결
    for i in range(10):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            print("✅ Kafka 연결 성공!")
            break
        except NoBrokersAvailable:
            print(f"⏳ Kafka 연결 대기 중... ({i + 1}/10)")
            time.sleep(2)

    if not producer:
        print("❌ Kafka 연결 실패. 종료")
        return

    # 2️⃣ 테스트용 종목
    stock_list = [
        {"code": "005930", "name": "삼성전자", "base_price": 75000},
        {"code": "000660", "name": "SK하이닉스", "base_price": 140000},
        {"code": "035420", "name": "NAVER", "base_price": 210000},
    ]

    print("📡 Mock 데이터 송신 시작 (Ctrl + C 로 종료)")

    try:
        while True:
            for stock in stock_list:
                fluctuation = random.randint(-1000, 1000)
                current_price = stock["base_price"] + fluctuation

                data = {
                    # 🔑 프론트에서 쓰는 필드명과 100% 일치
                    "stock_code": stock["code"],
                    "stock_name": stock["name"],
                    "current_price": current_price,

                    # ⚠️ 반드시 숫자 timestamp (ms)
                    "timestamp": int(time.time() * 1000),

                    # 가격 정보
                    "diff": fluctuation,
                    "rate": round(fluctuation / stock["base_price"] * 100, 2),

                    # 부가 정보
                    "open_price": stock["base_price"],
                    "high_price": current_price + random.randint(100, 500),
                    "low_price": current_price - random.randint(100, 500),
                    "tick_volume": random.randint(100, 5000),
                    "accumulated_vol": random.randint(100000, 500000),
                }

                producer.send(TOPIC_STOCK_TICKS, value=data)
                print(
                    f"📤 [Sent] {stock['name']}({stock['code']}): "
                    f"{current_price}원 ({data['rate']}%)"
                )

            producer.flush()
            time.sleep(2)  # ⏱ 2초 주기

    except KeyboardInterrupt:
        print("\n🛑 Mock Producer 종료")
        producer.close()


if __name__ == "__main__":
    run_mock_producer()
