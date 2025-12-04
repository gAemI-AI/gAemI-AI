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

        
    def parse_stock_data(self, raw_message):
        """
        Raw data:
        0|H0STCNT0|001|005930^101243^103700^5^-800^-0.77^103716.91^103900^104300^103200^103700^103600^264^3424539^355182644350^12149^15531^3382^76.90^1714627^1318567^1^0.39^23.30^090003^5^-200^090459^5^-600^094921^2^500^20251204^20^N^7687^5365^194754^398361^0.06^5337951^64.15^0^^103900
        """

        try:
            # 1. | 로 분리 (헤더 분리)
            parts = raw_message.split('|')
            if len(parts) < 4:
                return None

            # 2. ^로 분리된 데이터 처리하기
            data = parts[3].split('^')

            # 3. 매핑
            parsed_data = {
                "stock_code": data[0],           # 종목코드 (005930)
                "time": data[1],                 # 체결시간 (101243)
                "current_price": int(data[2]),   # 현재가 (103700) -> 숫자로 변환
                "diff": int(data[4]),            # 대비 (-800)
                "rate": float(data[5]),          # 등락률 (-0.77)
                "open_price": int(data[7]),      # 시가
                "high_price": int(data[8]),      # 고가
                "low_price": int(data[9]),       # 저가
                "tick_volume": int(data[12]),    # 체결량 (264)
                "accumulated_vol": int(data[13]) # 누적거래량
            }

            return parsed_data

        except Exception as e:
            logger.error(f"❌ 파싱 에러: {e} / Raw: {raw_message[:30]}...")
            return None

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
                        # 1. 파싱하기
                        json_data = self.parse_stock_data(message)

                        if json_data:
                            # 2. kafka로 쏘기 (JSON형태로)
                            self.producer.send(KAFKA_TOPIC_TICKS, json_data)

                            # 로그로 확인
                            logger.info(f"🚀 Kafka 전송: {json_data['stock_code']} | {json_data['current_price']}원")
                        
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