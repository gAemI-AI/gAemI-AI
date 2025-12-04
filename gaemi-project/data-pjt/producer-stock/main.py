import asyncio
import json
import logging
import requests
import websockets
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from config import *
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockProducer:
    def __init__(self):
        # Kafka 연결 대기 (최대 30초) -> Producer가 먼저 실행되어 연결 실패하는 경우를 위해 kafka가 살아날 때까지 연결 시도
        logger.info("Kafka 연결 대기 중...")
        max_retries = 30
        for i in range(max_retries):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=KAFKA_BROKER,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    api_version=(2, 5, 0),
                    retries=5,
                    request_timeout_ms=10000,
                    max_block_ms=10000
                )
                logger.info("✅ Kafka 연결 성공!")
                break
            except NoBrokersAvailable:
                if i < max_retries - 1:
                    logger.info(f"⏳ Kafka 대기 중... ({i+1}/{max_retries})")
                    time.sleep(2)
                else:
                    logger.error("❌ Kafka 연결 실패 (Timeout)")
                    raise
        
        self.approval_key = None
        
        # 구독 정보 저장 (TR_ID별 구분)
        self.subscriptions = {
            "H0STCNT0": [],  # 체결가
            "H0STASP0": [],  # 호가
            "H0UPCNT0": []   # 지수
        }

    def get_approval_key(self):
        """KIS WebSocket 접속에 필요한 Approval Key 발급"""
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
            logger.info(f"Approval Key 발급 성공: {self.approval_key[:10]}...")
        
        # 에러 처리     
        except Exception as e:
            logger.error(f"❌ Approval Key 발급 실패: {e}")
            raise

    def get_user_subscriptions(self):
        """
        [TODO] DB에서 유저들이 구독한 종목/지수 목록 가져오기
        
        예상 DB 쿼리 결과:
        [
            {"type": "stock-tick", "code": "005930"},
            {"type": "stock-tick", "code": "000660"},
            {"type": "stock-orderbook", "code": "005930"},
            {"type": "index-tick", "code": "001"}  # KOSPI
        ]
        """
        # 임시: 하드코딩된 구독 목록 (추후 DB 쿼리로 대체)
        return [
            {"type": "stock-tick", "code": "005930"},      # 삼성전자 체결가
            {"type": "stock-orderbook", "code": "005930"}, # 호가
            {"type": "index-tick", "code": "0001"},        # KOSPI 지수 
            {"type": "index-tick", "code": "1001"}         # KOSDAQ 지수 
        ]

    def parse_stock_tick(self, raw_message):
        """
        실시간 체결가 파싱 (H0STCNT0)
        
        Raw format: 0|H0STCNT0|001|005930^101243^103700^5^-800^-0.77^...
        """
        try:
            parts = raw_message.split('|')
            if len(parts) < 4:
                return None

            data = parts[3].split('^')
            
            # 시간을 timestamp로 변환 (HHMMSS -> Epoch ms)
            time_str = data[1]  # "101243"
            today = datetime.now().strftime("%Y%m%d")
            dt = datetime.strptime(f"{today}{time_str}", "%Y%m%d%H%M%S")
            timestamp = int(dt.timestamp() * 1000)

            parsed_data = {
                "stock_code": data[0], # 종목 코드
                "timestamp": timestamp, # 체결 시간
                "current_price": int(data[2]), # 현재가
                "diff": int(data[4]), # 전일대비 부호
                "rate": float(data[5]), # 등락률 (전일 대비율)
                "open_price": int(data[7]), # 시가
                "high_price": int(data[8]), # 고가
                "low_price": int(data[9]), # 저가
                "tick_volume": int(data[12]), # 이번 체결량
                "accumulated_vol": int(data[13]) # 누적 거래량
            }

            return parsed_data

        except Exception as e:
            logger.error(f"❌ 체결가 파싱 에러: {e} / Raw: {raw_message[:50]}...")
            return None

    def parse_stock_orderbook(self, raw_message):
        """
        실시간 호가 파싱 (H0STASP0)
        
        Raw format: 0|H0STASP0|001|005930^094530^82100^82000^100^500^...
        
        호가는 1~10호가까지 있음:
        - ASKP1~ASKP10 (매도 호가)
        - BIDP1~BIDP10 (매수 호가)
        - ASKP_RSQN1~10 (매도 잔량)
        - BIDP_RSQN1~10 (매수 잔량)
        """
        try:
            parts = raw_message.split('|')
            if len(parts) < 4:
                return None

            data = parts[3].split('^')
            
            # 시간 변환
            time_str = data[1]  # "094530"
            today = datetime.now().strftime("%Y%m%d")
            dt = datetime.strptime(f"{today}{time_str}", "%Y%m%d%H%M%S")
            timestamp = int(dt.timestamp() * 1000)

            # 매도 호가 (1~10호가) 구조화
            ask_levels = []
            for i in range(10):
                price_idx = 12 + i  # ASKP1부터 시작 인덱스
                vol_idx = 32 + i    # ASKP_RSQN1부터 시작 인덱스
                
                if len(data) > vol_idx:
                    ask_levels.append({
                        "price": int(data[price_idx]),
                        "volume": int(data[vol_idx])
                    })

            # 매수 호가 (1~10호가) 구조화
            bid_levels = []
            for i in range(10):
                price_idx = 22 + i  # BIDP1부터 시작 인덱스
                vol_idx = 42 + i    # BIDP_RSQN1부터 시작 인덱스
                
                if len(data) > vol_idx:
                    bid_levels.append({
                        "price": int(data[price_idx]),
                        "volume": int(data[vol_idx])
                    })

            parsed_data = {
                "stock_code": data[0], # 종목 코드
                "timestamp": timestamp, # 호가 시간
                "total_ask_volume": int(data[3]),  # TOTAL_ASKP_RSQN (총 매도 잔량)
                "total_bid_volume": int(data[4]),  # TOTAL_BID_RSQN (총 매수 잔량)
                "best_ask_price": int(data[12]),   # ASKP1 (매도 1호가)
                "best_bid_price": int(data[22]),   # BIDP1 (매수 1호가)
                "ask_levels": ask_levels,          # 매도 1~10호가 배열 (JSON Array)
                "bid_levels": bid_levels           # 매수 1~10호가 배열 (JSON Array)
            }

            return parsed_data

        except Exception as e:
            logger.error(f"❌ 호가 파싱 에러: {e} / Raw: {raw_message[:50]}...")
            return None

    def parse_index_tick(self, raw_message):
        """
        실시간 지수 파싱 (H0UPCNT0)
        
        Raw format: 0|H0UPCNT0|001|0001^094530^2540.50^12.50^0.49^5000000^...
        
        지수 코드:
        - 0001: KOSPI
        - 1001: KOSDAQ
        - 2001: KOSPI200
        """
        try:
            parts = raw_message.split('|')
            if len(parts) < 4:
                return None

            data = parts[3].split('^')
            
            # 시간 변환
            time_str = data[1]  # "094530"
            today = datetime.now().strftime("%Y%m%d")
            dt = datetime.strptime(f"{today}{time_str}", "%Y%m%d%H%M%S")
            timestamp = int(dt.timestamp() * 1000)

            parsed_data = {
                "index_code": data[0],                  # "0001" (KOSPI)
                "timestamp": timestamp,
                "current_value": float(data[2]),        # 현재 지수
                "change_value": float(data[3]),         # 대비
                "change_rate": float(data[4]),          # 등략률(%)
                "volume": int(data[5])                  # 거래량
            }

            return parsed_data

        except Exception as e:
            logger.error(f"❌ 지수 파싱 에러: {e} / Raw: {raw_message[:50]}...")
            return None

    async def subscribe(self, websocket, tr_id, tr_key):
        """개별 구독 요청 전송"""
        subscribe_data = {
            "header": {
                "approval_key": self.approval_key,
                "custtype": "P",
                "tr_type": "1",  # 1: 등록
                "content-type": "utf-8"
            },
            "body": {
                "input": {
                    "tr_id": tr_id,
                    "tr_key": tr_key
                }
            }
        }
        
        await websocket.send(json.dumps(subscribe_data))
        logger.info(f"구독 요청: {tr_id} - {tr_key}")

    async def connect_websocket(self):
        """WebSocket 연결 및 데이터 수신"""
        
        async with websockets.connect(KIS_WS_URL) as websocket:
            logger.info("✅ KIS WebSocket 연결 성공!")

            # 1. DB에서 구독 목록 가져오기
            user_subscriptions = self.get_user_subscriptions()
            
            # 2. 구독 요청 전송
            for sub in user_subscriptions:
                # stock-tick (실시간 시세)
                if sub["type"] == "stock-tick":
                    await self.subscribe(websocket, "H0STCNT0", sub["code"])
                    self.subscriptions["H0STCNT0"].append(sub["code"])

                # stock-orderbook (호가) 
                elif sub["type"] == "stock-orderbook":
                    tr_key = f"{sub['code']}"
                    await self.subscribe(websocket, "H0STASP0", tr_key)
                    self.subscriptions["H0STASP0"].append(sub["code"])

                
                # index-tick (지수)    
                elif sub["type"] == "index-tick":
                    await self.subscribe(websocket, "H0UPCNT0", sub["code"])
                    self.subscriptions["H0UPCNT0"].append(sub["code"])

            # 3. 데이터 수신 루프
            while True:
                try:
                    message = await websocket.recv()
                    
                    # 디버깅: 모든 메시지 앞 100글자 출력
                    logger.info(f"👀 [RAW]: {message[:100]}")
                    
                    # 실시간 데이터 판별 (첫 글자 0 또는 1)
                    if message[0] in ['0', '1']:
                        await self.process_realtime_data(message)
                        
                    else:
                        # JSON 시스템 메시지
                        try:
                            data = json.loads(message)
                            tr_id = data.get('header', {}).get('tr_id')

                            if tr_id == 'PINGPONG':
                                await websocket.send(message)
                                logger.info(f"🏓 PINGPONG 응답")
                            else:
                                logger.info(f"🔔 시스템 메시지: {data}")
                        except json.JSONDecodeError:
                            logger.warning(f"⚠️ 알 수 없는 메시지: {message[:50]}")

                except websockets.ConnectionClosed:
                    logger.error("❌ WebSocket 연결 끊김")
                    break
                except Exception as e:
                    logger.error(f"⚠️ 데이터 수신 중 에러: {e}")

    async def process_realtime_data(self, raw_message):
        """실시간 데이터 처리 및 Kafka 전송"""
        try:
            # TR_ID 추출 (형식: 0|H0STCNT0|001|...)
            parts = raw_message.split('|')
            if len(parts) < 2:
                logger.warning(f"⚠️ 잘못된 데이터 형식: {raw_message[:50]}")
                return
            
            tr_id = parts[1]
            # 디버깅 확인
            logger.info(f"데이터 수신: TR_ID={tr_id}")  
            
            # TR_ID에 따른 파서 호출
            if tr_id == "H0STCNT0":
                # 체결가
                logger.info(f"#################### 체결가 파싱 시도... ####################") 
                parsed = self.parse_stock_tick(raw_message)
                if parsed:
                    self.producer.send(KAFKA_TOPIC_TICKS, parsed)
                    logger.info(f"체결가: {parsed['stock_code']} - {parsed['current_price']}원")
                else:
                    logger.warning(f"⚠️ 체결가 파싱 실패") 
                    
            elif tr_id == "H0STASP0":
                # 호가
                logger.info(f"#################### 호가 파싱 시도... ####################") 
                parsed = self.parse_stock_orderbook(raw_message)
                if parsed:
                    self.producer.send(KAFKA_TOPIC_ORDERBOOK, parsed)
                    logger.info(f"호가: {parsed['stock_code']} - 매도:{parsed['best_ask_price']} / 매수:{parsed['best_bid_price']}")
                else:
                    logger.warning(f"⚠️ 호가 파싱 실패")  
                    
            elif tr_id == "H0UPCNT0":  
                # 지수
                logger.info(f"#################### 지수 파싱 시도... ####################") 
                parsed = self.parse_index_tick(raw_message)
                if parsed:
                    self.producer.send(KAFKA_TOPIC_INDEX, parsed)
                    logger.info(f"지수: {parsed['index_code']} - {parsed['current_value']}")
                else:
                    logger.warning(f"⚠️ 지수 파싱 실패") 
                    
            else:
                logger.warning(f"⚠️ 알 수 없는 TR_ID: {tr_id}")
                
        except Exception as e:
            logger.error(f"❌ 실시간 데이터 처리 에러: {e}", exc_info=True)  # ✅ 스택 트레이스 추가

    def run(self):
        """Producer 실행"""
        self.get_approval_key()
        asyncio.get_event_loop().run_until_complete(self.connect_websocket())

if __name__ == "__main__":
    print("🚀 Stock Producer 시작...")
    producer = StockProducer()
    producer.run()