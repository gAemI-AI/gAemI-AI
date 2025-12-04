# data-pjt/producer-stock/main.py
import asyncio
import json
import logging
import requests
import websockets
from kafka import KafkaProducer
from config import *

# 로깅 설정 (Docker 로그에서 확인하기 위함)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockProducer:
    def __init__(self):
        # 1. Kafka Producer 초기화
        # config.py에서 KAFKA_BROKER (kafka:29092) 가져옴
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(2, 5, 0), # Kafka 연결 안정성을 위한 버전 명시
            retries=5
        )
        self.approval_key = None

    def get_approval_key(self):
        """KIS WebSocket 접속에 필요한 Approval Key 발급 (HTTP)"""
        url = f"{KIS_BASE_URL}/oauth2/Approval"
        headers = {"content-type": "application/json; utf-8"}
        body = {
            "grant_type": "client_credentials",
            "appkey": KIS_APP_KEY,
            "secretkey": KIS_APP_SECRET
        }
        
        try:
            res = requests.post(url, headers=headers, data=json.dumps(body))
            res.raise_for_status()
            self.approval_key = res.json()["approval_key"]
            logger.info(f"🔑 Approval Key 발급 성공: {self.approval_key[:10]}...")
        except Exception as e:
            logger.error(f"❌ Approval Key 발급 실패: {e}")
            raise

    async def connect_websocket(self):
        """WebSocket 연결 및 데이터 수신"""
        # 테스트용으로 '삼성전자(005930)' 강제 구독
        stock_code = "005930" 

        # 웹소켓 연결 시작
        async with websockets.connect(KIS_WS_URL) as websocket:
            logger.info("✅ KIS WebSocket 연결 성공!")

            # 1. 구독 요청 메시지 전송 (JSON)
            subscribe_data = {
                "header": {
                    "approval_key": self.approval_key,
                    "custtype": "P",
                    "tr_type": "1", # 1: 등록(Subscribe)
                    "content-type": "utf-8"
                },
                "body": {
                    "input": {
                        "tr_id": "H0STCNT0",  # 실시간 주식 체결가 TR ID
                        "tr_key": stock_code  # 종목코드
                    }
                }
            }
            await websocket.send(json.dumps(subscribe_data))
            logger.info(f"📡 [{stock_code}] 구독 요청 전송 완료")

            # 2. 무한 루프로 데이터 수신
            while True:
                try:
                    message = await websocket.recv()
                    
        
                    # [디버깅용] 무조건 출력해보기
                    logger.info(f"👀 [RAW 데이터 도착]: {message}")  

                    # 데이터 종류 판별
                    # 첫 글자가 0 또는 1이면 실시간 데이터 (암호화 여부)
                    if message[0] in ['0', '1']: 
                        # Kafka로 보낼 메시지 구성
                        # (나중에 여기서 파싱 로직을 추가하여 포맷 정의서대로 변환)
                        kafka_data = {
                            "type": "stock-tick",
                            "raw_data": message # 실제는 파싱된 데이터 넣어야 함 (현재는 테스트라 전체 데이터)
                        }
                        
                        # Kafka 'stock-ticks' 토픽으로 전송
                        self.producer.send(KAFKA_TOPIC_TICKS, kafka_data)
                        self.producer.flush() # 즉시 전송 강제
                        
                    else:
                        # JSON 형태의 시스템 메시지 (구독 성공, PINGPONG 등)
                        try:
                            data = json.loads(message)
                            tr_id = data.get('header', {}).get('tr_id')

                            if tr_id == 'PINGPONG':
                                # 핑퐁 메시지는 로그만 찍고 넘어감 (데이터 아님)
                                await websocket.send(message)

                                logger.info(f"🏓 PINGPONG 수신")
                            else:
                                logger.info(f"🔔 시스템 메시지: {data}")
                        except:
                            logger.info(f"알 수 없는 메시지: {message}")

                except websockets.ConnectionClosed:
                    logger.error("❌ WebSocket 연결 끊김. 재연결 시도 필요.")
                    break
                except Exception as e:
                    logger.error(f"⚠️ 데이터 수신 중 에러: {e}")
                    break

    def run(self):
        # 1. 키 발급
        self.get_approval_key()
        # 2. 웹소켓 실행
        asyncio.get_event_loop().run_until_complete(self.connect_websocket())

if __name__ == "__main__":
    print("🚀 Stock Producer 시작...")
    producer = StockProducer()
    producer.run()