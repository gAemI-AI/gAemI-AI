# data-pjt/producer-news/main.py
import time
import json
import logging
import feedparser
import schedule
import hashlib
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic  # 관리자 도구 임포트
from kafka.errors import TopicAlreadyExistsError    # 에러 임포트
from config import *
from datetime import datetime

# docker내에서 로그 확인을 위한 장치
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsProducer:
    def __init__(self):
        # 토픽 자동 생성 및 설정 (Compact 모드)
        self.create_topic_if_not_exists()

        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(2, 5, 0),
            retries=5
        )
        # 중복 방지용 (URL 해시 저장)
        self.processed_ids = set()
        
        # 수집할 종목 목록 (나중엔 DB로 연동)
        self.target_keywords = [
            {"code": "005930", "name": "삼성전자"},
            {"code": "000660", "name": "SK하이닉스"},
            {"code": "035420", "name": "NAVER"},
            {"code": "005380", "name": "현대차"}
        ]

    # 토픽 생성 로직 (토픽 청소 정책 설정을 위해)
    def create_topic_if_not_exists(self):
        try:
            # Admin Client 연결
            admin_client = KafkaAdminClient(
                bootstrap_servers=KAFKA_BROKER,
                api_version=(2, 5, 0)
            )
            
            # 현재 토픽 목록 가져오기
            existing_topics = admin_client.list_topics()
            
            # 아직 해당 토픽이 존재하지 않는다면
            if KAFKA_TOPIC_NEWS not in existing_topics:
                logger.info(f"토픽 '{KAFKA_TOPIC_NEWS}' 생성 중 (Log Compaction 적용)...")
                
                # 토픽 설정 정의
                topic_list = [NewTopic(
                    name=KAFKA_TOPIC_NEWS, 
                    num_partitions=1, 
                    replication_factor=1,
                    # 청소 정책을 하이브리드로 설정
                    # kafka 토픽은 시간이 지나면 삭제가 기본 'Compact'는 최신 상태만 남기는 Update 방식
                    # 두가지 모두 적용
                    topic_configs={'cleanup.policy': 'delete, compact'}
                )]
                
                admin_client.create_topics(new_topics=topic_list, validate_only=False)
                logger.info(f"✅ 토픽 '{KAFKA_TOPIC_NEWS}' 생성 완료!")
            else:
                logger.info(f"ℹ️ 토픽 '{KAFKA_TOPIC_NEWS}' 이미 존재함. 생성 건너뜀.")
                
            admin_client.close()
            
        except Exception as e:
            logger.error(f"⚠️ 토픽 생성 중 오류 (이미 존재할 수 있음): {e}")


    def generate_id(self, link):
        """URL을 기반으로 고유 ID 생성 (MD5 해시)"""
        return hashlib.md5(link.encode('utf-8')).hexdigest()

    def fetch_and_send(self):
        logger.info("뉴스 수집 시작...")
        
        for target in self.target_keywords:
            stock_name = target['name']
            stock_code = target['code']
            
            # 1. RSS 데이터 가져오기
            rss_url = RSS_URL_FORMAT.format(stock_name)
            feed = feedparser.parse(rss_url)
            
            if not feed.entries: # feed.entries는 리스트 형태
                continue

            count = 0

            # 2. 각 뉴스 항목 파싱
            for entry in feed.entries:
                """
                {
                    'title': '삼성전자, 역대 최대 매출 기록… 반도체 회복세',
                    'link': 'https://news.google.com/articles/xxxxx',
                    'summary': '삼성전자가 올해 4분기 역대 최대 실적을 기록했다...',
                    'published': 'Mon, 02 Dec 2024 09:15:00 GMT',
                    'published_parsed': time.struct_time(...),
                    'source': {
                        'title': '한국경제'
                    }
                }

                """
                # 중복 방지를 위한 뉴스 아이디 생성
                news_id = self.generate_id(entry.link)
                
                # 이미 보낸 뉴스면 건너뛰기 (중복 제거)
                if news_id in self.processed_ids:
                    continue
                
                # 아직 보내지 않은 뉴스면 전송

                # 3. 데이터 포맷팅
                published_struct = entry.get('published_parsed') #published_parsed: RSS 피드에서 제공하는 날짜, 시간 정보

                if published_struct:
                    # feedparser는 time.struct_time(Unix timestap) 객체로 변환해줌
                    timestamp = int(time.mktime(published_struct) * 1000) # kafka, DB에 넣기 좋은 숫자 형태로 변환
                else: # 정보가 없다면
                    timestamp = int(time.time() * 1000) # 현재 시간으로 주입

                news_data = {
                    "news_id": news_id,
                    "stock_code": stock_code,
                    "title": entry.title,
                    "link": entry.link,
                    "source": entry.get('source', {}).get('title', 'Google News'),
                    "published_at": timestamp,
                    "crawled_at": int(time.time() * 1000) # 현재 시간
                }

                # 4. Kafka 전송
                # key를 설정하여 Log Compaction 활용 가능하게 함
                self.producer.send(
                    KAFKA_TOPIC_NEWS, 
                    key=news_id.encode('utf-8'), 
                    value=news_data
                )
                
                self.processed_ids.add(news_id)
                count += 1
            
            if count > 0:
                logger.info(f"✅ [{stock_name}] 새 뉴스 {count}건 전송 완료")
        
        self.producer.flush()

    def run(self):
        # 최초 실행
        self.fetch_and_send()
        
        # 주기적 실행 등록
        schedule.every(CRAWL_INTERVAL).seconds.do(self.fetch_and_send)
        
        logger.info(f"🚀 News Producer 시작 (주기: {CRAWL_INTERVAL}초)")
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    producer = NewsProducer()
    producer.run()