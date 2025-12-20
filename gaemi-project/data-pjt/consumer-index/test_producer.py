import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime

# Docker 내부에서 실행할 것이므로 호스트는 'kafka:29092'
BROKER = 'kafka:29092'
TOPIC = 'index-ticks'

def get_random_data():
    timestamp = int(time.time() * 1000) # 현재 시간 (ms)
    
    # KOSPI (0001) 가짜 데이터
    kospi = {
        "index_code": "0001",
        "timestamp": timestamp,
        "current_value": round(random.uniform(2550.0, 2650.0), 2), # 2550 ~ 2650 사이 랜덤
        "change_value": round(random.uniform(-20.0, 20.0), 2),
        "change_rate": round(random.uniform(-1.5, 1.5), 2),
        "volume": random.randint(300000, 500000)
    }

    # KOSDAQ (1001) 가짜 데이터
    kosdaq = {
        "index_code": "1001",
        "timestamp": timestamp,
        "current_value": round(random.uniform(800.0, 900.0), 2),
        "change_value": round(random.uniform(-10.0, 10.0), 2),
        "change_rate": round(random.uniform(-2.0, 2.0), 2),
        "volume": random.randint(100000, 200000)
    }
    
    return [kospi, kosdaq]

def run_mock_producer():
    print(f"🚀 Mock Producer 시작 (Target: {TOPIC})")
    
    producer = None
    while not producer:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[BROKER],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            print("✅ Kafka 연결 성공!")
        except Exception as e:
            print(f"⏳ 연결 대기 중... ({e})")
            time.sleep(2)

    try:
        while True:
            data_list = get_random_data()
            for data in data_list:
                producer.send(TOPIC, value=data)
                print(f"Testing [Sent] {data['index_code']} : {data['current_value']}")
            
            time.sleep(5) 

    except KeyboardInterrupt:
        print("🛑 테스트 종료")
        producer.close()

if __name__ == "__main__":
    run_mock_producer()