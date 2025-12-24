"""
Kafka Bridge - Kafka 토픽을 구독하고 WebSocket으로 클라이언트에 전송
"""
import json
import asyncio
from kafka import KafkaConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class KafkaBridge:
    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.kafka_broker = getattr(settings, 'KAFKA_BROKER', 'kafka:9092')
        self.consumers = {}

    def start_alert_consumer(self):
        """
        alert 토픽을 구독하고 WebSocket으로 전송
        Kafka 메시지 형식:
        {
            "user_id": "1",
            "message": "삼성전자 목표가 80,000원 도달! (현재: 80,100원)"
        }
        """
        def consume_alerts():
            try:
                consumer = KafkaConsumer(
                    'alert',
                    bootstrap_servers=[self.kafka_broker],
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    auto_offset_reset='latest',
                    group_id='websocket-alert-group',
                    enable_auto_commit=True,
                )
                logger.info("✅ Alert Consumer 시작")
                
                for message in consumer:
                    try:
                        alert_data = message.value
                        user_id = alert_data.get('user_id')
                        alert_msg = alert_data.get('message')
                        
                        if user_id and alert_msg:
                            # WebSocket 그룹으로 전송
                            async_to_sync(self.channel_layer.group_send)(
                                f"user_{user_id}",
                                {
                                    'type': 'send_alert',
                                    'message': alert_msg
                                }
                            )
                            logger.info(f"🚀 [Alert] User {user_id}: {alert_msg}")
                    except Exception as e:
                        logger.error(f"❌ Alert 처리 중 에러: {e}")
            except Exception as e:
                logger.error(f"❌ Alert Consumer 에러: {e}")

        import threading
        thread = threading.Thread(target=consume_alerts, daemon=True)
        thread.start()

    def start_stock_tick_consumer(self):
        """
        stock-ticks 토픽을 구독하고 WebSocket으로 전송
        Kafka 메시지 형식:
        {
            "code": "005930",
            "price": 76000,
            "rate": 2.5,
            "timestamp": 1709000000000
        }
        """
        def consume_ticks():
            try:
                consumer = KafkaConsumer(
                    'stock-ticks',
                    bootstrap_servers=[self.kafka_broker],
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    auto_offset_reset='latest',
                    group_id='websocket-stock-group',
                    enable_auto_commit=True,
                )
                logger.info("✅ Stock Ticks Consumer 시작")
                
                for message in consumer:
                    try:
                        tick_data = message.value
                        stock_code = tick_data.get('code')
                        
                        if stock_code:
                            # WebSocket 그룹으로 전송
                            async_to_sync(self.channel_layer.group_send)(
                                f"stock_{stock_code}",
                                {
                                    'type': 'send_chart_data',
                                    'data': tick_data
                                }
                            )
                            logger.info(f"📈 [Stock Tick] {stock_code}: {tick_data['price']}원 ({tick_data.get('rate', 0)}%)")
                    except Exception as e:
                        logger.error(f"❌ Stock Tick 처리 중 에러: {e}")
            except Exception as e:
                logger.error(f"❌ Stock Ticks Consumer 에러: {e}")

        import threading
        thread = threading.Thread(target=consume_ticks, daemon=True)
        thread.start()

    def start_all_consumers(self):
        """모든 Kafka 컨슈머 시작"""
        logger.info("🔄 Kafka Bridge 컨슈머 시작 중...")
        
        # alert 컨슈머 시작
        try:
            self.start_alert_consumer()
        except Exception as e:
            logger.error(f"❌ Alert Consumer 실패: {e}")
        
        # stock-ticks 컨슈머 시작
        try:
            self.start_stock_tick_consumer()
        except Exception as e:
            logger.error(f"❌ Stock Ticks Consumer 실패: {e}")
        
        logger.info("✅ Kafka Bridge 모든 컨슈머 시작됨")


# 글로벌 인스턴스
kafka_bridge = KafkaBridge()
