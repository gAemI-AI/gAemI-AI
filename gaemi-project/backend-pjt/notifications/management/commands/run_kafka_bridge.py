import json
import asyncio
from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from kafka import KafkaConsumer

class Command(BaseCommand):
    help = 'Consume Kafka messages and push to WebSocket groups'

    def handle(self, *args, **options):
        # 파이썬 출력 버퍼링 비활성화 (로그 즉시 출력)
        import sys
        sys.stdout.reconfigure(line_buffering=True)
        
        self.stdout.write(self.style.SUCCESS('🚀 Kafka-WebSocket Bridge Started...'))
        
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.consume_loop())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('🛑 Bridge Stopped.'))

    async def consume_loop(self):
        channel_layer = get_channel_layer()

        # [MVP 배포용 설정]
        # 1. group_id 고정: 서버 재시작 시 중복 수신 방지
        # 2. auto_offset_reset='latest': 과거 데이터 폭주 방지 (실시간만 처리)
        consumer = KafkaConsumer(
            'alert', 'stock-ticks',
            bootstrap_servers=['kafka:29092'],
            group_id='websocket-bridge-group',  # 고정된 그룹 ID
            auto_offset_reset='latest',         # 최신 데이터만 수신
            enable_auto_commit=True
        )

        self.stdout.write(self.style.SUCCESS('✅ Listening to Kafka topics: alert, stock-ticks'))

        for message in consumer:
            try:
                raw_value = message.value
                if not raw_value:
                    continue
                
                # JSON 디코딩
                decoded_str = raw_value.decode('utf-8')
                data = json.loads(decoded_str)
                
                topic = message.topic

                # [Case A] 알림 메시지 (NotificationProcessor.py와 키 일치)
                if topic == 'alert':
                    user_id = data.get('user_id')
                    alert_msg = data.get('message')
                    
                    if user_id:
                        group_name = f"user_{user_id}"
                        await channel_layer.group_send(
                            group_name,
                            {'type': 'send_alert', 'message': alert_msg}
                        )
                        # 로그: 너무 많으면 주석 처리
                        print(f"📢 [Alert Push] User {user_id}: {alert_msg}")

                # [Case B] 실시간 주식 데이터 (StockProducer.py와 일치)
                elif topic == 'stock-ticks':
                    # Producer 키: 'stock_code', 'current_price', 'rate'
                    stock_code = data.get('stock_code')  
                    current_price = data.get('current_price') 
                    rate = data.get('rate')
                    
                    if stock_code:
                        group_name = f"stock_{stock_code}"
                        
                        # 프론트엔드에 보낼 데이터 포맷팅
                        payload = {
                            "code": stock_code,
                            "price": current_price,
                            "rate": rate,
                            "timestamp": data.get('timestamp')
                        }

                        await channel_layer.group_send(
                            group_name,
                            {
                                'type': 'send_chart_data',
                                'data': payload
                            }
                        )
                        # print(f"📈 [Stock Push] {stock_code}: {current_price}")

            except json.JSONDecodeError:
                pass 
            except Exception as e:
                print(f"❌ Bridge Error: {e}")