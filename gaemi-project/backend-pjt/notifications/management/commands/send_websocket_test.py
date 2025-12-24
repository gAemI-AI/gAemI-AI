"""
관리 명령어: Kafka에 테스트 데이터 전송
사용법: python manage.py send_websocket_test
"""
import json
import time
from django.core.management.base import BaseCommand
from kafka import KafkaProducer
from django.conf import settings


class Command(BaseCommand):
    help = 'Kafka에 WebSocket 테스트 데이터 전송'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='all',
            choices=['alert', 'stock', 'all'],
            help='전송할 데이터 타입 (alert, stock, all)'
        )

    def handle(self, *args, **options):
        kafka_broker = getattr(settings, 'KAFKA_BROKER', 'kafka:9092')
        data_type = options['type']

        try:
            producer = KafkaProducer(
                bootstrap_servers=[kafka_broker],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Kafka 연결 성공: {kafka_broker}"))

            # 알림 테스트 데이터 전송
            if data_type in ['alert', 'all']:
                alert_data = {
                    "user_id": "1",
                    "message": "삼성전자 목표가 80,000원 도달! (현재: 80,100원)"
                }
                producer.send('alert', alert_data)
                self.stdout.write(self.style.SUCCESS(f"🚀 Alert 전송: {alert_data}"))
                time.sleep(1)

            # 주식 틱 테스트 데이터 전송
            if data_type in ['stock', 'all']:
                stocks = [
                    {"code": "005930", "price": 76000, "rate": 2.5, "timestamp": int(time.time() * 1000)},
                    {"code": "000660", "price": 102000, "rate": -1.2, "timestamp": int(time.time() * 1000)},
                    {"code": "051910", "price": 58000, "rate": 0.8, "timestamp": int(time.time() * 1000)},
                ]
                
                for stock in stocks:
                    producer.send('stock-ticks', stock)
                    self.stdout.write(self.style.SUCCESS(f"📈 Stock Tick 전송: {stock}"))
                    time.sleep(0.5)

            producer.flush()
            self.stdout.write(self.style.SUCCESS("✅ 모든 테스트 데이터 전송 완료"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Kafka 연결 실패: {e}"))
