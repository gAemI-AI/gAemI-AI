import json
import time
import random
import sys
import os
from datetime import datetime

# config.py 경로 인식을 위해 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from config import KAFKA_BROKER, TOPIC_STOCK_TICKS

def run_mock_producer():
    print(f"🚀 [Mock] 가짜 주식 데이터 생성기 시작")
    print(f"👉 Target Kafka: {KAFKA_BROKER}")
    print(f"👉 Target Topic: {TOPIC_STOCK_TICKS}")

    producer = None
    
    # 1. Kafka 연결 시도
    for i in range(10):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("✅ Kafka 연결 성공!")
            break
        except NoBrokersAvailable:
            print(f"⏳ Kafka 연결 대기 중... ({i+1}/10)")
            time.sleep(2)
    
    if not producer:
        print("❌ Kafka 연결 실패. 종료합니다.")
        return

    # 2. 가짜 데이터 무한 발송
    stock_list = [
        {"code": "005930", "name": "삼성전자", "base_price": 75000},
        {"code": "000660", "name": "SK하이닉스", "base_price": 140000},
        {"code": "035420", "name": "NAVER", "base_price": 210000},
    ]

    try:
        while True:
            for stock in stock_list:
                # 가격 변동 (랜덤)
                fluctuation = random.randint(-1000, 1000)
                current_price = stock["base_price"] + fluctuation
                
                data = {
                    "stock_code": "005930",
                    "stock_name": "삼성전자",
                    "current_price": 75000,
                    "timestamp": datetime.now().isoformat(),
                    # 👇 아래 필드들이 빠져서 경고가 뜨는 것임! (0이라도 넣어야 함)
                    "diff": 1000,
                    "rate": 1.5,
                    "open_price": 74000,
                    "high_price": 75500,
                    "low_price": 73500,
                    "tick_volume": 100,
                    "accumulated_vol": 500000
                    }
                
                producer.send(TOPIC_STOCK_TICKS, value=data)
                print(f"📤 [Sent] {stock['name']}({stock['code']}): {current_price}원")
            
            producer.flush()
            time.sleep(2) # 2초마다 발송

    except KeyboardInterrupt:
        print("\n🛑 중단됨")
        producer.close()

if __name__ == "__main__":
    run_mock_producer()