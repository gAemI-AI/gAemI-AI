import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URL에서 user_id 추출 (/ws/notifications/<user_id>/)
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"user_{self.user_id}"

        # 그룹 가입
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        # 👇 연결 성공 로그 (이게 떠야 WebSocket 연결된 것임)
        print(f"🔌 [WebSocket Connected] User: {self.user_id} (Channel: {self.channel_name})")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print(f"🔌 [WebSocket Disconnected] User: {self.user_id}")

    # Kafka Bridge에서 보낸 메시지 받기
    async def send_alert(self, event):
        message = event['message']
        
        # 클라이언트로 전송
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'data': message
        }))
        print(f"🚀 [Sent to Client] {message}")

class ChartConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.stock_code = self.scope['url_route']['kwargs']['stock_code']
        self.group_name = f"stock_{self.stock_code}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        print(f"📈 [Chart WS Connected] Stock: {self.stock_code}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_chart_data(self, event):
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'chart_update',
            'data': data
        }))