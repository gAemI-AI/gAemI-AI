# data-pjt/flink-jobs/setup_kafka.py
# Flink Job이 시작되기 전, Kafka 브로커가 살아있는지 확인 후
# 필요한 토픽들을 미리 생성하는 초기화 스크립트

import time
import sys
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import NoBrokersAvailable, TopicAlreadyExistsError

KAFKA_BROKER = "gaemi_kafka:29092"
REQUIRED_TOPICS = ["stock-ticks", "stock-orderbook", "index-ticks", "alert"]

def wait_for_kafka_and_init():
    print(f"🛠️ [Setup] Kafka({KAFKA_BROKER}) 연결 및 토픽 생성 시도...")
    
    admin_client = None
    max_retries = 30  # 최대 30번 시도
    
    for i in range(max_retries):
        try:
            # 1. 연결 시도
            admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BROKER) # 실패 시 바로 except(NoBrokersAvailable)로 감
            print("✅ [Setup] Kafka 연결 성공!")
            
            # 2. 토픽 생성
            existing_topics = admin_client.list_topics()
            new_topics = []
            
            for topic in REQUIRED_TOPICS:
                if topic not in existing_topics:
                    new_topics.append(NewTopic(name=topic, num_partitions=1, replication_factor=1))
            
            if new_topics:
                admin_client.create_topics(new_topics)
                print(f"✨ [Setup] 새 토픽 생성 완료: {len(new_topics)}개")
            else:
                print("👍 [Setup] 모든 토픽이 이미 존재합니다.")
                
            admin_client.close()
            return True # 성공
            
        except NoBrokersAvailable:
            print(f"⏳ [Setup] Kafka 부팅 대기 중... ({i+1}/{max_retries})")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ [Setup] 예기치 않은 오류 (재시도 함): {e}")
            time.sleep(2)
    
    print("❌ [Setup] Kafka 연결 실패 (Timeout)")
    return False # 실패

if __name__ == "__main__":
    if not wait_for_kafka_and_init():
        sys.exit(1) # 실패 시 컨테이너 종료 코드로 빠져나감