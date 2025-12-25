# data-pjt/flink-jobs/notification_processor.py
# 실시간 주식 알림 처리: kafka에서 실시간 주가를 받아 사용자가 설정한 알림 조건(DB)과 비교 후 알림 발송

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer, KafkaSink, KafkaRecordSerializationSchema
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import WatermarkStrategy, RestartStrategies
from pyflink.datastream.functions import MapFunction 
from pyflink.common.typeinfo import Types

import json
import time
from datetime import datetime
import sys
import os

# Docker 컨테이너 내 로컬 모듈(config, utils)를 찾기 위한 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 사용자 정의 모듈 import
from config import (
    KAFKA_BROKER, TOPIC_STOCK_TICKS, TOPIC_ALERT, 
    GROUP_ID_NOTIFICATION, RULE_RELOAD_INTERVAL_SECONDS, ALERT_COOLDOWN_SECONDS
)
from utils.db_connector import load_active_rules, save_triggered_notification, check_recent_alert

class NotificationProcessor(MapFunction):
    def __init__(self):
        self.rules = [] # DB에서 가져온 알림 규칙을 저장할 리스트 (메모리 캐시)
        self.last_load_time = 0 # 마지막으로 규칙을 로딩한 시간 (주기적 갱신)
        self.reload_interval = RULE_RELOAD_INTERVAL_SECONDS # 규칙 갱신 시간 

    def open(self, runtime_context):
        """
        생명주기: Job이 시작될 때 한 번 실행되는 함수, 데이터 처리를 시작하지 전에 DB에서 초기 규칙 미리 로딩
        """
        print("[Processor] Worker 시작 및 규칙 로딩")
        self._load_rules()
    
    def _load_rules(self):
        """
        도우미: DB에서 활성화된 알림 규칙을 가져와서 메모리에 저장
        """
        try:
            self.rules = load_active_rules() # db_connector.py의 함수 호출
            self.last_load_time = time.time() # 로딩 시간 기록
            print(f"[Rules] 현재 활성 규칙: {len(self.rules)}개")
            sys.stdout.flush() # 로그 즉시 출력
        except Exception as e:
            print(f"❌ [Rules Load Error] {e}")
            sys.stdout.flush()
    
    def map(self, value):
        """
        메인 함수: Kafka에서 데이터가 들어올 때 마다 실행됨
        e.g., value: '{'stock_code': "005930", 'current_price': 75000}'
        """
        try:
            # 1. 규칙 갱신 주기 체크: 규칙 갱신 시간이 지났으면 DB에서 다시 로드
            if time.time() - self.last_load_time > self.reload_interval:
                self._load_rules()
            
            # 2. 들어온 문자열 데이터 JSON으로 변환
            stock_data = json.loads(value)
            stock_code = stock_data.get('stock_code')
            price = float(stock_data.get('current_price', 0))
            
            if not stock_code or price == 0: return None # 데이터가 비정상이면 None 반환 (나중에 filter로 걸러짐)
            
            # 3. 메모리에 있는 모든 알림 규칙을 하나씩 검사 (순회)
            for rule in self.rules:
                # 규칙의 종목코드와 현재 들어온 주식 종목코드가 다르면 패스
                if rule['stock_id'] != stock_code: continue
                
                # 조건 비교 준비
                target = float(rule['target_value'])
                op = rule['operator']

                # 4. 실제 가격 비교 로직
                is_triggered = (op == '>=' and price >= target) or \
                               (op == '<=' and price <= target) or \
                               (op == '==' and abs(price - target) < 0.01)
                
                # 5. 조건이 만족되었다면 -> 알림 발생
                if is_triggered:
                    # 최근 1분(60초) 내에 이미 알림을 보냈는지 확인
                    if check_recent_alert(rule['rule_id'], ALERT_COOLDOWN_SECONDS):
                        print(f"      쿨타임 중: {rule['stock_name']}")
                        continue
                    
                    # 알림 메시지 생성 (더 나은 형식)
                    operator_text = {
                        '>=': '이상',
                        '<=': '이하',
                        '==': '도달'
                    }.get(op, op)
                    
                    msg = f"🚀 {rule['stock_name']} {operator_text} {target:,.0f}원 달성! (현재: {price:,.0f}원)"
                    
                    # 6. DB에 알림 발송 내역 저장 (성공 시 알림 ID 반환)
                    noti_id = save_triggered_notification(rule['user_id'], rule['rule_id'], rule['stock_name'], msg)
                    
                    if noti_id:
                        print(f"    [알림 발송 & DB 저장 완료] ID: {noti_id}")
                        sys.stdout.flush()

                        # 7. kafka 'alert' 토픽으로 보낼 데이터 반환 (이 반환값은 main 함수 sink로 전달됨)
                        return json.dumps({
                            'notification_id': noti_id,
                            'user_id': rule['user_id'],
                            'message': msg,
                            'timestamp': datetime.now().isoformat()
                        }, ensure_ascii=False)
            return None # 맞는 규칙이 하나도 없으면 None 반환
        
        except Exception as e:
            print(f"❌ [Process Error] {e}")
            sys.stdout.flush()
            return None

# -----------------------------------------------------------
# 메인 함수 (Flink Job 토폴로지 정의)
# : 전체 파이프라인(Source -> Process -> Sink)을 조립
# -----------------------------------------------------------
def main():
    # 1. 실행 환경 생성
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1) # 순서 보장을 위해 병렬 처리를 1개로 제한
    
    # 에러가 나면 5초(5000ms) 쉬었다가 최대 100번까지 재시작
    # DB가 잠깐 끊기거나 Kafka가 늦게 뜰 때 죽지 않도록 함
    env.set_restart_strategy(RestartStrategies.fixed_delay_restart(
        100,  # 최대 100번 재시도
        5000  # 5000ms 대기
    ))

    # 2. Source 설정
    # -> Kafka의 'stock-ticks' 토픽에서 데이터를 읽어옴
    stock_source = KafkaSource.builder() \
        .set_bootstrap_servers(KAFKA_BROKER) \
        .set_topics(TOPIC_STOCK_TICKS) \
        .set_group_id(GROUP_ID_NOTIFICATION) \
        .set_starting_offsets(KafkaOffsetsInitializer.latest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()
    
    # 3. Sink 설정
    # -> 처리된 알림을 Kafka의 'alert' 토픽으로 보냄
    alert_sink = KafkaSink.builder() \
        .set_bootstrap_servers(KAFKA_BROKER) \
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic(TOPIC_ALERT)
            .set_value_serialization_schema(SimpleStringSchema())
            .build()
        ) \
        .build()
    
    # 4. 파이프라인 연결 (Data Flow)
    env.from_source(stock_source, WatermarkStrategy.no_watermarks(), "Stock Source") \
        .map(NotificationProcessor(), output_type=Types.STRING()) \
        .filter(lambda x: x is not None) \
        .sink_to(alert_sink)

    print("🚀 Flink Job Started...")
    sys.stdout.flush()
    env.execute("Notification Job")

if __name__ == "__main__":
    main()